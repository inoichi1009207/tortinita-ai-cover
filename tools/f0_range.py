"""对给定音频测唱段音域(P10/中位/P90)。用法: f0_range.py <wav> [<wav>...]"""
import sys, numpy as np, librosa, os
NOTES = "C C# D D# E F F# G G# A A# B".split()
def nn(hz):
    m = int(round(69 + 12 * np.log2(hz / 440))); return f"{NOTES[m % 12]}{m // 12 - 1}"
for p in sys.argv[1:]:
    y, sr = librosa.load(p, sr=22050, mono=True)
    f0, v, pr = librosa.pyin(y, fmin=100, fmax=900, sr=sr, frame_length=2048)
    f0 = f0[~np.isnan(f0)]
    name = os.path.basename(p)[:14]
    if len(f0) < 50:
        print(f"{name}: 有声帧不足({len(f0)})"); continue
    lo, med, hi = np.percentile(f0, 10), np.median(f0), np.percentile(f0, 90)
    print(f"{name}: 有声帧={len(f0)} P10 {lo:.0f}Hz({nn(lo)}) | 中位 {med:.0f}Hz({nn(med)}) | P90 {hi:.0f}Hz({nn(hi)})")
