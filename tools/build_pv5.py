"""PV v5 = PV v3 + 身体不动只动嘴(全片用同姿势对 srchr012 闭嘴 / srchr151 张嘴,像素差:身体 0.0、头 0.3)+ 嘴型只在音节起点切换(onset)且最短保持 0.25s。
PV v3 = PV v2 + 歌词层(pv/lyrics_timed.json,每行一张透明 PNG,0.25s 淡入/0.4s 淡出,底部居中)。
PV v2:封面帧(无人)开头 10s / 结尾 8s;中段 8 场景 = 背景 CG + 扎发朵朵;张嘴/闭嘴按人声包络逐帧切换(30fps);场景间 1s 交叉淡;
帧由 numpy 直接喂 ffmpeg(rawvideo 管道),输出 yuv420p H.264;音频缺省 goodbye_torta_final_v2.mp3(argv[1] 可换)。
在 clipboard/ai-cover/ 下执行:venv/Scripts/python.exe tools/build_pv3.py [音频] [输出](缺省输出 pv/draft_pv_v3_lyrics.mp4)"""
import subprocess, sys, os, numpy as np, librosa
from PIL import Image
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
AUDIO = sys.argv[1] if len(sys.argv) > 1 else 'goodbye_torta_final_v2.mp3'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'pv/draft_pv_v5_still_body.mp4'
W, H, FPS = 1920, 1080, 30; TOTAL = 218.86; INTRO = 10.0; OUTRO = 8.0; XF = 1.0
def bg(name): return Image.open(f'pv/assets/bg/{name}.png').convert('RGB').resize((W, H), Image.LANCZOS)
def comp(b, sprite, scale=2.25, xr=140, yo=0):
    c = b.convert('RGBA'); sp = Image.open(f'pv/assets/sprites/{sprite}.png').convert('RGBA')
    sp = sp.resize((int(sp.width * scale), int(sp.height * scale)), Image.LANCZOS)
    c.alpha_composite(sp, (W - sp.width - xr, H - sp.height + yo)); return np.asarray(c.convert('RGB'), dtype=np.uint8)
from PIL import ImageDraw, ImageFont
import json
LYR = json.load(open('pv/lyrics_timed.json', encoding='utf-8'))
font = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', 60)
def lyric_png(text):
    im = Image.new('RGBA', (W, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im); bb = d.textbbox((0, 0), text, font=font); x = (W - bb[2]) // 2
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (2, 2), (-2, -2)): d.text((x + dx, 8 + dy), text, font=font, fill=(0, 0, 0, 200))
    d.text((x, 8), text, font=font, fill=(255, 255, 255, 255)); return np.asarray(im, dtype=np.float32)
LYR_IMG = [lyric_png(o['text']) for o in LYR]
LY = H - 190  # 歌词条顶边
def lyric_alpha(t):
    for o, img in zip(LYR, LYR_IMG):
        if o['t'] - 0.25 <= t <= o['t_end'] + 0.4:
            a = min(1.0, (t - (o['t'] - 0.25)) / 0.25, (o['t_end'] + 0.4 - t) / 0.4); return img, max(0.0, a)
    return None, 0.0
cover = np.asarray(Image.open('pv/cover.jpg').convert('RGB').resize((W, H)), dtype=np.uint8)
# (背景, 闭嘴立绘, 张嘴立绘) —— 只用扎发朵朵;张嘴 = 013 / 122 / 151
scenes = [(b, 'srchr012', 'srchr151') for b in ['srbg184', 'srbg026', 'srbg054', 'srbg305', 'srbg165', 'srbg284', 'srbg354', 'srbg024']]
mid = TOTAL - INTRO - OUTRO; per = mid / len(scenes)
frames = [(comp(bg(b), c), comp(bg(b), o)) for b, c, o in scenes]
# 人声包络 → 嘴型:帧 RMS 高于 −32 dBFS 为张嘴;持续张嘴每 0.32 s 插 2 帧闭嘴模拟音节
y, sr = librosa.load('leadB_fly235.wav', sr=22050, mono=True, offset=6.594); hop = sr // FPS
nfr = int(TOTAL * FPS)
rms = np.array([np.sqrt(np.mean(y[k * hop:(k + 1) * hop] ** 2)) if (k + 1) * hop <= len(y) else 0 for k in range(nfr)])
voiced = 20 * np.log10(rms + 1e-9) > -32
# 音节起点:onset 检测(源轴 → 成品轴已由 offset 处理),在起点处闭嘴 2 帧;其余时间有声即张嘴;最短保持 0.25s
on_frames = set(int(round(t_ * FPS)) for t_ in librosa.frames_to_time(librosa.onset.onset_detect(y=y, sr=sr, hop_length=512, backtrack=False, delta=0.07, wait=8), sr=sr, hop_length=512))
openm = voiced.copy(); MIN_HOLD = int(0.25 * FPS)
for k in sorted(on_frames):
    if 0 < k < nfr and voiced[k]: openm[k - 1:k + 1] = False
# 去掉短于 MIN_HOLD 的张嘴/闭嘴碎段(除 onset 闭嘴 2 帧外)
k = 0
while k < nfr:
    j = k
    while j < nfr and openm[j] == openm[k]: j += 1
    if j - k < MIN_HOLD and not (not openm[k] and j - k <= 2):
        openm[k:j] = not openm[k]
    k = j
toggles = int(np.sum(openm[1:] != openm[:-1])); print('嘴型切换次数 %d,每分钟 %.0f' % (toggles, toggles / (TOTAL / 60)))
def seg_at(t):
    if t < INTRO or t >= TOTAL - OUTRO: return ('cover', None, 0)
    i = min(int((t - INTRO) // per), len(scenes) - 1); return ('scene', i, (t - INTRO) - i * per)
def frame_of(kind, i, k):
    if kind == 'cover': return cover
    c, o = frames[i]; return o if openm[k] else c
proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', AUDIO,
                         '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-preset', 'medium', '-crf', '20', '-movflags', '+faststart',
                         '-c:a', 'aac', '-b:a', '256k', '-shortest', OUT], stdin=subprocess.PIPE)
for k in range(nfr):
    t = k / FPS; kind, i, local = seg_at(t); img = frame_of(kind, i, k).astype(np.float32)
    if kind == 'scene' and local > per - XF:  # 场景尾 1 s 与下一段交叉淡
        a = (local - (per - XF)) / XF; nxt = frame_of('scene', i + 1, k) if i + 1 < len(scenes) else cover
        img = img * (1 - a) + nxt.astype(np.float32) * a
    elif kind == 'cover' and INTRO - XF < t < INTRO:
        a = (t - (INTRO - XF)) / XF; img = img * (1 - a) + frame_of('scene', 0, k).astype(np.float32) * a
    li, la = lyric_alpha(t)
    if li is not None and la > 0:
        reg = img[LY:LY + 120]; al = (li[:, :, 3:4] / 255.0) * la; img[LY:LY + 120] = reg * (1 - al) + li[:, :, :3] * al
    if t < 1.5: img *= t / 1.5
    if t > TOTAL - 2.5: img *= max(0.0, (TOTAL - t) / 2.5)
    proc.stdin.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())
proc.stdin.close(); proc.wait()
print('ffmpeg exit', proc.returncode, '张嘴帧占比 %.2f' % openm.mean())
