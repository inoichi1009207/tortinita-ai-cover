"""PV v7:按用户给的「歌词行区间 → 图片」分配表切镜;sran 竖排帧条按帧循环播放(8 fps,雨/云动画),srbg 静图;每镜头慢推 4%;镜头间 0.8s 叠化;歌词层同 v3。
分配表写在 PLAN(行号按 pv/lyrics.lrc,1 起;'cover' = pv/cover.jpg)。用法:venv/Scripts/python.exe tools/build_pv7.py [音频] [输出]"""
import subprocess, sys, os, json, numpy as np
from PIL import Image, ImageDraw, ImageFont
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
AUDIO = sys.argv[1] if len(sys.argv) > 1 else 'goodbye_torta_final_v3.mp3'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'pv/draft_pv_v7.mp4'
W, H, FPS = 1920, 1080, 30; TOTAL = 218.86; XF = 0.8; ZOOM = 0.04; ANIM_FPS = 8
PLAN = [(1, 2, 'cover'), (3, 6, 'srbg054'), (7, 10, 'sran074c'), (11, 13, 'srbg026'), (14, 17, 'srbg296'), (18, 20, 'srbg266'), (21, 24, 'sran176b'),
        (25, 31, 'sran195b'), (32, 38, 'sran184a'), (39, 40, 'sran370a'), (41, 43, 'sran352a')]
LYR = json.load(open('pv/lyrics_timed.json', encoding='utf-8'))
BOUND = [0.0] + [LYR[a - 1]['t'] for a, b, n in PLAN[1:]] + [TOTAL]
def frames_of(name):
    if name == 'cover': return [Image.open('pv/cover.jpg').convert('RGB')]
    im = Image.open(f'pv/assets/bg_all/{name}.png').convert('RGB')
    if name.startswith('sran'): return [im.crop((0, i * 480, 640, (i + 1) * 480)) for i in range(im.height // 480)]
    return [im]
BIG = {n: [f.resize((int(W * (1 + ZOOM)) + 2, int(H * (1 + ZOOM)) + 2), Image.LANCZOS) for f in frames_of(n)] for _, _, n in PLAN}
def frame_shot(i, local, dur, t):
    frs = BIG[PLAN[i][2]]; big = frs[int(t * ANIM_FPS) % len(frs)]; p = min(1.0, local / max(dur, 1e-6)); z = 1 + ZOOM * (1 - p)
    cw, ch = int(W * z), int(H * z); x0 = (big.width - cw) // 2; y0 = (big.height - ch) // 2
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
nfr = int(TOTAL * FPS)
proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', AUDIO,
                         '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-preset', 'veryfast', '-crf', '20', '-movflags', '+faststart',
                         '-c:a', 'aac', '-b:a', '256k', '-shortest', OUT], stdin=subprocess.PIPE)
for k in range(nfr):
    t = k / FPS; i = max(j for j in range(len(PLAN)) if BOUND[j] <= t); dur = BOUND[i + 1] - BOUND[i]; local = t - BOUND[i]
    img = frame_shot(i, local, dur, t)
    if i + 1 < len(PLAN) and local > dur - XF:
        a = (local - (dur - XF)) / XF; img = img * (1 - a) + frame_shot(i + 1, 0.0, BOUND[i + 2] - BOUND[i + 1], t) * a
    li, la = lyric_alpha(t)
    if li is not None and la > 0:
        reg = img[LY:LY + 120]; al = (li[:, :, 3:4] / 255.0) * la; img[LY:LY + 120] = reg * (1 - al) + li[:, :, :3] * al
    if t < 1.5: img *= t / 1.5
    if t > TOTAL - 2.5: img *= max(0.0, (TOTAL - t) / 2.5)
    proc.stdin.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())
proc.stdin.close(); proc.wait()
print('ffmpeg exit', proc.returncode); print('镜头表:'); [print(f"  行 {a}-{b} {n:9s} {BOUND[i]:7.2f} → {BOUND[i+1]:7.2f}  ({BOUND[i+1]-BOUND[i]:5.1f}s)") for i, (a, b, n) in enumerate(PLAN)]
