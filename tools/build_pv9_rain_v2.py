"""PV v9 rain-v2 candidate: traced pane masks + eight advected rain phases.
Run: venv/Scripts/python.exe tools/build_pv9_rain_v2.py [audio] [output]
Default path rebuilds A+B through rain_v2.build_assets (usage counter in metrics).
Retire/retrace when backgrounds or fixed framing change. v8 lyrics/cuts retained.
"""
import subprocess, sys, os, json, numpy as np
from PIL import Image, ImageDraw, ImageFont
from rain_v2 import build_assets, rain_at, PANES
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
AUDIO = sys.argv[1] if len(sys.argv) > 1 else 'goodbye_torta_final_20260904.mp3'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'pv/pv_v9_rain_v2.mp4'
W, H, FPS = 1920, 1080, 30; TOTAL = 218.86; XF = 0.8; ANIM_FPS = 8; RAIN_ALPHA = 0.8
PLAN = [(1, 2, 'cover'), (3, 6, 'srbg054'), (7, 10, 'sran074c'), (11, 13, 'srbg026'), (14, 17, 'srbg296'), (18, 20, 'srbg266'), (21, 24, 'sran176b'),
        (25, 31, 'sran195b'), (32, 38, 'sran184a'), (39, 40, 'sran370a'), (41, 43, 'sran352a')]
LYR = json.load(open('pv/lyrics_timed.json', encoding='utf-8'))
BOUND = [0.0] + [LYR[a - 1]['t'] for a, b, n in PLAN[1:]] + [TOTAL]
build_assets()
RAIN = [np.asarray(Image.open(f'pv/assets/rain/streak8_{k}.png').convert('RGBA'), dtype=np.float32)[..., 3] / 255 * RAIN_ALPHA for k in range(1, 9)]

def sky_mask(bg, name=None):
    with Image.open(f'pv/assets/masks/{name}.png') as mask:
        if mask.mode != 'L' or mask.size != (W, H):
            raise ValueError(f'{name}: expected a 1920x1080 L mask')
        return np.asarray(mask, dtype=np.float32) / 255
SHOT = {}
for _, _, name in PLAN:
    if name in SHOT: continue
    if name == 'cover':
        bg = Image.open('pv/cover.jpg').convert('RGB'); SHOT[name] = {'frames': [np.asarray(bg, dtype=np.float32)], 'rain': 'full'}
    elif name.startswith('sran'):
        im = Image.open(f'pv/assets/bg_all/{name}.png').convert('RGB'); n = im.height // 480
        SHOT[name] = {'frames': [np.asarray(im.crop((0, i * 480, 640, (i + 1) * 480)).resize((W, H), Image.LANCZOS), dtype=np.float32) for i in range(n)], 'rain': 'light'}
    else:
        bg = Image.open(f'pv/assets/bg_all/{name}.png').convert('RGB').resize((W, H), Image.LANCZOS)   # 只取 RGB,忽略游戏自带 alpha
        SHOT[name] = {'frames': [np.asarray(bg, dtype=np.float32)], 'rain': 'mask' if name in PANES else 'full'}
        if name in PANES: SHOT[name]['mask'] = sky_mask(bg, name)
def frame_shot(i, t):
    s = SHOT[PLAN[i][2]]; k = int(t * ANIM_FPS); img = s['frames'][k % len(s['frames'])]
    if s['rain'] is None: return img.copy()   # 必须拷贝:歌词层是就地写进 img 的,直接返回缓存帧会把上一句歌词残留在缓存里(v8 首渲 40s 处出现叠影)
    a = rain_at(RAIN, t)
    if s['rain'] == 'mask': a = a * s['mask']
    elif s['rain'] == 'light': a = a * 0.45   # sran 条自带雨帧,只补一层淡的
    a = a[..., None]; return img * (1 - a) + 255 * a
font = ImageFont.truetype('msyhbd.ttc', 60)
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
    img = frame_shot(i, t)
    if i + 1 < len(PLAN) and local > dur - XF:
        a = (local - (dur - XF)) / XF; img = img * (1 - a) + frame_shot(i + 1, t) * a
    li, la = lyric_alpha(t)
    if li is not None and la > 0:
        reg = img[LY:LY + 120]; al = (li[:, :, 3:4] / 255.0) * la; img[LY:LY + 120] = reg * (1 - al) + li[:, :, :3] * al
    if t < 1.5: img = img * (t / 1.5)
    if t > TOTAL - 2.5: img = img * max(0.0, (TOTAL - t) / 2.5)
    proc.stdin.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())
proc.stdin.close(); proc.wait(); print('ffmpeg exit', proc.returncode)
