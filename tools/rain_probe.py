"""雨层探针:对比成片某时刻的帧与游戏动画条各原帧,报窗区最小平均绝对差(MAD)。
用法:venv/Scripts/python.exe tools/rain_probe.py <mp4> <秒> <条名> [x0 y0 x1 y1]
无雨时 MAD 只剩缩放+压缩噪声(经验 <4);叠了雨丝 MAD 明显更高。判据线由 2026-09-05 在 v10(有雨)上实测标定。"""
import sys, subprocess, numpy as np
from PIL import Image
mp4, t, name = sys.argv[1], float(sys.argv[2]), sys.argv[3]
box = tuple(int(v) for v in sys.argv[4:8]) if len(sys.argv) >= 8 else (0, 0, 700, 400)
raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', mp4, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True, check=True).stdout
fr = np.frombuffer(raw, dtype=np.uint8).reshape(1080, 1920).astype(np.float32)
im = Image.open(f'pv/assets/bg_all/{name}.png').convert('L'); n = im.height // 480
x0, y0, x1, y1 = box
mads = [np.abs(fr[y0:y1, x0:x1] - np.asarray(im.crop((0, i * 480, 640, (i + 1) * 480)).resize((1920, 1080), Image.LANCZOS), dtype=np.float32)[y0:y1, x0:x1]).mean() for i in range(n)]
print(f'{name} t={t} box={box} minMAD={min(mads):.2f} frame={int(np.argmin(mads))+1}')
