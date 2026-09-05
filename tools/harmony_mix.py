"""女和声压低 + 朵朵抬高(2026-09-04 用户:「和声还是大,只有女和声;调大朵朵」)。
输入:stems-inst/inst_full_down2_(Vocals|Instrumental)_*.wav(karaoke 模型把 −2 半音的官方伴奏拆成 和声轨 / 纯伴奏),leadB_fly235_107.wav。
做法:和声轨逐秒测 F0 中位,>240 Hz 判女声区 → 该秒增益 g(argv 给 dB),男声区/无和声 = 1;增益曲线 0.3 s 平滑;
      新伴奏 = 纯伴奏 + 和声轨×增益 → 走 v4a 混音链(主唱 +5 dB,比原来 +1;伴奏 −2 dB + 250 Hz −2 + 侧链 2:1),响度对齐 −12 LUFS。
用法:venv/Scripts/python.exe tools/harmony_mix.py <女和声 dB,如 -4> <标签>  →  goodbye_torta_final_<标签>.mp3 + clips/<标签>_*.mp3"""
import sys, os, glob, subprocess, numpy as np, librosa, soundfile as sf
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
GDB = float(sys.argv[1]); TAG = sys.argv[2]
bv = glob.glob('stems-inst/inst_full_down2_(Vocals)*.wav')[0]; pi = glob.glob('stems-inst/inst_full_down2_(Instrumental)*.wav')[0]
b, sr = sf.read(bv, always_2d=True); p, sr2 = sf.read(pi, always_2d=True); assert sr == sr2
n = min(len(b), len(p)); b, p = b[:n], p[:n]
mono = b.mean(axis=1).astype(np.float32); sec = int(np.ceil(n / sr))
# 女声区判定缓存(pyin 逐秒太慢——首跑 10 分钟没跑完;改 yin,并把判定存 json 复用)
import json
CACHE = 'stems-inst/female_seconds.json'
WIN = sys.argv[3] if len(sys.argv) > 3 else ''
if WIN: female = set()          # 只压指定窗口 ⇒ 根本不用判女声区(用户:「那十秒钟逐秒不就好了」——窗口给定时连逐秒都不用)
elif os.path.exists(CACHE): female = set(json.load(open(CACHE)))
else:
    female = set(); m22 = librosa.resample(mono, orig_sr=sr, target_sr=22050)
    for s in range(sec):
        seg = m22[s * 22050:(s + 1) * 22050]
        if len(seg) < 11025 or 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9) < -45: continue
        f0 = librosa.yin(seg, fmin=80, fmax=800, sr=22050, frame_length=2048)
        rms = librosa.feature.rms(y=seg, frame_length=2048, hop_length=512)[0]; f0 = f0[:len(rms)][rms[:len(f0)] > 0.01]
        if len(f0) and np.median(f0) > 240: female.add(s)
    json.dump(sorted(female), open(CACHE, 'w'))
gain = np.ones(sec)
# WIN 已在上面定义   # 可选:只压指定窗口,如 "62.5-69.5,146.5-160.5"(成品轴秒);给了就不按女声区判
if WIN:
    env_w = np.ones(n)
    for w in WIN.split(','):
        a, b_ = map(float, w.split('-')); env_w[int(a * sr):int(b_ * sr)] = 10 ** (GDB / 20)
    female = set(); print(f'只压窗口 {WIN}')
else:
    for s in female: gain[s] = 10 ** (GDB / 20)
env = env_w if WIN else np.repeat(gain, sr)[:n]
if len(env) < n: env = np.pad(env, (0, n - len(env)), constant_values=1.0)
k = int(0.3 * sr); c = np.cumsum(np.pad(env, (k // 2, k - k // 2), mode='edge')); env = (c[k:] - c[:-k]) / k   # O(n) 滑动平均;np.convolve 在 960 万点上是 O(n·k),跑了 7 分钟没完
inst = p + b * env[:, None]
out_inst = f'inst_full_down2_{TAG}.wav'; sf.write(out_inst, inst, sr, subtype='PCM_16')
fem = int((gain < 1).sum()); print(f'女声区秒数 {fem}/{sec},增益 {GDB} dB;新伴奏 → {out_inst}')
VOL_V = "volume=eval=frame:volume='if(between(t,157.3,162.0),0.841,if(between(t,157.15,157.3),1-0.159*(t-157.15)/0.15,if(between(t,162.0,162.15),0.841+0.159*(t-162.0)/0.15,1)))'"
VOL_I = "volume=eval=frame:volume='if(between(t,157.3,162.0),1.259,if(between(t,157.15,157.3),1+0.259*(t-157.15)/0.15,if(between(t,162.0,162.15),1.259-0.259*(t-162.0)/0.15,1)))'"
raw = f'{TAG}_raw.mp3'
fc = (f"[0:a]atrim=start=6.594,asetpts=PTS-STARTPTS,volume={os.environ.get("LEAD_DB","5")}dB,aresample=44100,{VOL_V},apad,asplit=2[v][sc];"
      f"[1:a]volume=-2dB,{VOL_I},equalizer=f=250:t=q:w=1.2:g=-2[i0];[i0][sc]sidechaincompress=threshold=0.1:ratio=2:attack=20:release=250:makeup=1:level_sc=1[i];"
      f"[v][i]amix=inputs=2:duration=shortest:normalize=0,alimiter=limit=0.98[out]")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'leadB_fly235_107.wav', '-i', out_inst, '-filter_complex', fc, '-map', '[out]', '-c:a', 'libmp3lame', '-b:a', '320k', raw], check=True)
r = subprocess.run(['ffmpeg', '-i', raw, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True)
import re; lufs = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1]); comp = round(-12.0 - lufs, 2)   # 取汇总行(最后一个);第一个匹配是 t=0 的逐帧读数 −70,曾据此补偿 +58 dB 把成品压成方波
final = f'goodbye_torta_final_{TAG}.mp3'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', f'volume={comp}dB,alimiter=limit=0.98', '-c:a', 'libmp3lame', '-b:a', '320k', final], check=True); os.remove(raw)
os.makedirs('clips', exist_ok=True)
for ss, name in ((60, '100-115'), (150, '230-245'), (170, '250-305')):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(ss), '-t', '15', '-i', final, '-c:a', 'libmp3lame', '-b:a', '192k', f'clips/{TAG}_{name}.mp3'], check=True)
r2 = subprocess.run(['ffmpeg', '-i', final, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True)
print(f'{final}: 原始 {lufs} LUFS → 补偿 {comp} dB → {re.findall(r"I:\s+(-?[\d.]+) LUFS", r2.stderr)[-1]} LUFS;片段 clips/{TAG}_*.mp3')
