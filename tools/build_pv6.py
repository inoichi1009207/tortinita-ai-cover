"""PV v6:无立绘,按官方 PV 转场统计仿制(官方:29 镜头、平均 7.7s、64% 硬切 / 36% 约 0.5s 叠化、48% 镜头带推拉)。
镜头切点 = 官方 LRC 行起点里间隔 ≥5.5s 的那些(+首尾);每镜头一张背景 CG(10 张循环)配一种运动(推近/右摇/拉远/左摇);
段落起点处用 0.5s 叠化,其余硬切;歌词层同 v3。参数:argv[1] 音频, argv[2] 输出。"""
import subprocess, sys, os, json, re, numpy as np
from PIL import Image, ImageDraw, ImageFont
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
AUDIO = sys.argv[1] if len(sys.argv) > 1 else 'goodbye_torta_final_v4a_FLY107_KEEP.mp3'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'pv/draft_pv_v6.mp4'
W, H, FPS = 1920, 1080, 30; TOTAL = 218.86; XF = 0.5; MIN_SHOT = 5.5; ZOOM = 0.08
SECTION = [34.16, 48.25, 62.17, 78.16, 91.09, 119.43, 133.01, 147.35, 162.98, 175.77, 203.65]
LYR = json.load(open('pv/lyrics_timed.json', encoding='utf-8'))
cuts = [0.0]
for o in LYR:
    if o['t'] - cuts[-1] >= MIN_SHOT: cuts.append(o['t'])
if TOTAL - cuts[-1] < 3: cuts.pop()
BOUND = cuts + [TOTAL]
BGS = ['srbg184', 'srbg026', 'srbg054', 'srbg305', 'srbg165', 'srbg284', 'srbg354', 'srbg296', 'srbg084', 'srbg024']
MOTIONS = ['zoom_in', 'pan_r', 'zoom_out', 'pan_l']
SHOTS = [('cover', 'zoom_in')] + [(BGS[i % len(BGS)], MOTIONS[i % 4]) for i in range(len(BOUND) - 3)] + [('cover', 'zoom_out')]
assert len(SHOTS) == len(BOUND) - 1, (len(SHOTS), len(BOUND))
def load(name): return Image.open('pv/cover.jpg' if name == 'cover' else f'pv/assets/bg/{name}.png').convert('RGB')
BIG = {n: load(n).resize((int(W * (1 + ZOOM)) + 2, int(H * (1 + ZOOM)) + 2), Image.LANCZOS) for n, _ in SHOTS}
def frame_shot(i, local, dur):
    name, mo = SHOTS[i]; big = BIG[name]; p = min(1.0, local / max(dur, 1e-6))
    if mo == 'zoom_in': z = 1 + ZOOM * (1 - p); cx = cy = 0.5
    elif mo == 'zoom_out': z = 1 + ZOOM * p; cx = cy = 0.5
    elif mo == 'pan_r': z = 1.0; cx = 0.5 + 0.5 * (p - 0.5) ; cy = 0.5   # 从左到右
    else: z = 1.0; cx = 0.5 - 0.5 * (p - 0.5); cy = 0.5
    cw, ch = int(W * z), int(H * z); x0 = int((big.width - cw) * cx); y0 = int((big.height - ch) * cy)
    x0 = min(max(x0, 0), big.width - cw); y0 = min(max(y0, 0), big.height - ch)
    return np.asarray(big.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR), dtype=np.float32)
font = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', 60)
def lyric_png(text):
    im = Image.new('RGBA', (W, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im); bb = d.textbbox((0, 0), text, font=font); x = (W - bb[2]) // 2
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (2, 2), (-2, -2)): d.text((x + dx, 8 + dy), text, font=font, fill=(0, 0, 0, 200))
    d.text((x, 8), text, font=font, fill=(255, 255, 255, 255)); return np.asarray(im, dtype=np.float32)
LYR_IMG = [lyric_png(o['text']) for o in LYR]; LY = H - 190
def lyric_alpha(t):
    for o, img in zip(LYR, LYR_IMG):
        if o['t'] - 0.25 <= t <= o['t_end'] + 0.4:
            return img, max(0.0, min(1.0, (t - (o['t'] - 0.25)) / 0.25, (o['t_end'] + 0.4 - t) / 0.4))
    return None, 0.0
is_section = [any(abs(b - s) < 0.3 for s in SECTION) for b in BOUND]
nfr = int(TOTAL * FPS)
proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', AUDIO,
                         '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-preset', 'veryfast', '-crf', '20', '-movflags', '+faststart',
                         '-c:a', 'aac', '-b:a', '256k', '-shortest', OUT], stdin=subprocess.PIPE)
for k in range(nfr):
    t = k / FPS
    i = max(j for j in range(len(SHOTS)) if BOUND[j] <= t); dur = BOUND[i + 1] - BOUND[i]; local = t - BOUND[i]
    img = frame_shot(i, local, dur)
    if i + 1 < len(SHOTS) and is_section[i + 1] and local > dur - XF:
        a = (local - (dur - XF)) / XF; img = img * (1 - a) + frame_shot(i + 1, 0.0, BOUND[i + 2] - BOUND[i + 1]) * a
    li, la = lyric_alpha(t)
    if li is not None and la > 0:
        reg = img[LY:LY + 120]; al = (li[:, :, 3:4] / 255.0) * la; img[LY:LY + 120] = reg * (1 - al) + li[:, :, :3] * al
    if t < 1.5: img *= t / 1.5
    if t > TOTAL - 2.5: img *= max(0.0, (TOTAL - t) / 2.5)
    proc.stdin.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())
proc.stdin.close(); proc.wait()
d = np.diff(BOUND); print('ffmpeg exit', proc.returncode, '镜头数', len(SHOTS), '平均镜头 %.1fs' % d.mean(), '叠化数', sum(is_section), '硬切数', len(SHOTS) - 1 - sum(is_section))
