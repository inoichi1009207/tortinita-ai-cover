"""PV v8:按用户分配表切镜(同 v7),**不缩放**;雨效 = 程序合成的斜向雨丝层(pv/assets/rain/streak_1..4.png,8 fps 循环;游戏动画条差分抽出的那层大头是地面涟漪,用户否掉):
封面与 sran 之外的静态外景全幅叠,静态室内只叠在窗外天空掩膜内(游戏本体室内也只在窗外见雨);sran 条本身带雨帧,原样播放。
镜头间 0.8s 叠化;歌词层同 v3。用法:venv/Scripts/python.exe tools/build_pv8.py [音频] [输出]"""
import subprocess, sys, os, json, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
AUDIO = sys.argv[1] if len(sys.argv) > 1 else 'goodbye_torta_final_20260904.mp3'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'pv/pv_v8_rain.mp4'
W, H, FPS = 1920, 1080, 30; TOTAL = 218.86; XF = 0.8; ANIM_FPS = 8; RAIN_ALPHA = 0.8
PLAN = [(1, 2, 'cover'), (3, 6, 'srbg054'), (7, 10, 'sran074c'), (11, 13, 'srbg026'), (14, 17, 'srbg296'), (18, 20, 'srbg266'), (21, 24, 'sran176b'),
        (25, 31, 'sran195b'), (32, 38, 'sran184a'), (39, 40, 'sran370a'), (41, 43, 'sran352a')]
LYR = json.load(open('pv/lyrics_timed.json', encoding='utf-8'))
BOUND = [0.0] + [LYR[a - 1]['t'] for a, b, n in PLAN[1:]] + [TOTAL]
RAIN = [np.asarray(Image.open(f'pv/assets/rain/streak_{k}.png').convert('RGBA').resize((W, H), Image.BILINEAR), dtype=np.float32)[..., 3] / 255 * RAIN_ALPHA for k in (1, 2, 3, 4)]
# 每张室内:窗框矩形 + 排除矩形(天花板/墙角漏雨处)+ 玻璃色判据(白天=浅灰天空;夜晚=深灰玻璃;窗棂浅色自然排除)。
# 用户 2026-09-04 目检:0:50 走廊天花板漏雨、1:04 卧室窗棂上有雨丝且玻璃有空洞 —— 由此改为 day/night 双判据 + 排除框。
SPEC = {
    'srbg054': {'rects': [(0, 0, 660, 880), (880, 140, 1450, 880)], 'excl': [(880, 140, 1010, 210)], 'mode': 'day'},
    'srbg026': {'rects': [(0, 0, 420, 810), (440, 150, 905, 810), (905, 470, 1155, 790)], 'excl': [(830, 140, 905, 290)], 'mode': 'day'},
    'srbg296': {'rects': [(250, 110, 1240, 700)], 'excl': [], 'mode': 'night'},
    'srbg266': {'rects': [(0, 100, 300, 620)], 'excl': [], 'mode': 'night'},
}
def sky_mask(bg, name=None):
    sp = SPEC.get(name, {'rects': [(0, 0, W, H)], 'excl': [], 'mode': 'day'})
    hsv = np.asarray(bg.convert('HSV'), dtype=np.float32); s = hsv[..., 1] / 255; v = hsv[..., 2] / 255
    glass = ((s < 0.16) & (v > 0.25) & (v < 0.9)) if sp['mode'] == 'day' else ((s < 0.25) & (v < 0.5))
    rm = np.zeros((H, W), dtype=bool)
    for x0, y0, x1, y1 in sp['rects']: rm[y0:y1, x0:x1] = True
    for x0, y0, x1, y1 in sp['excl']: rm[y0:y1, x0:x1] = False
    m = Image.fromarray(((glass & rm).astype(np.uint8) * 255)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.5))
    return np.asarray(m, dtype=np.float32) / 255
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
        SHOT[name] = {'frames': [np.asarray(bg, dtype=np.float32)], 'rain': 'mask', 'mask': sky_mask(bg, name)}
def frame_shot(i, t):
    s = SHOT[PLAN[i][2]]; k = int(t * ANIM_FPS); img = s['frames'][k % len(s['frames'])]
    if s['rain'] is None: return img.copy()   # 必须拷贝:歌词层是就地写进 img 的,直接返回缓存帧会把上一句歌词残留在缓存里(v8 首渲 40s 处出现叠影)
    a = RAIN[k % 4]
    if s['rain'] == 'mask': a = a * s['mask']
    elif s['rain'] == 'light': a = a * 0.45   # sran 条自带雨帧,只补一层淡的
    a = a[..., None]; return img * (1 - a) + 255 * a
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
