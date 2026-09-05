"""和声轨逐秒诊断:RMS 能量 + pyin 中位基频 → 建议路由(male→Chris / female→Torta /
   silence→门限掉 / uncertain→人耳裁)。产物 dataset/harmony_route.csv + 合并段落表打印。
   判据天花板:男女同刻叠唱时 pyin 只报一个主导基频,这类段会被误标单一性别——
   置信列低于阈值的段一律标 uncertain 交人耳。"""
import csv, sys
import numpy as np
import librosa

SRC = r"D:\test\clipboard\ai-cover\stems-lead\goodbye_src_(Vocals)_model_bs_roformer_ep_317_sdr_12_(Instrumental)_mel_band_roformer_karaoke_aufr33_viperx_sdr_10.flac"
OUT = r"D:\test\clipboard\ai-cover\dataset\harmony_route.csv"

y, sr = librosa.load(SRC, sr=22050, mono=True)
hop = sr // 2  # 0.5s 块
n = len(y) // hop
f0, voiced, vprob = librosa.pyin(y, fmin=65, fmax=500, sr=sr, frame_length=2048)
t_f0 = librosa.times_like(f0, sr=sr, hop_length=512)

rows = []
for i in range(n):
    t0, t1 = i * 0.5, (i + 1) * 0.5
    seg = y[i * hop:(i + 1) * hop]
    rms_db = 20 * np.log10(max(np.sqrt(np.mean(seg ** 2)), 1e-8))
    m = (t_f0 >= t0) & (t_f0 < t1) & ~np.isnan(f0)
    med = float(np.median(f0[m])) if m.any() else 0.0
    conf = float(np.mean(vprob[(t_f0 >= t0) & (t_f0 < t1)])) if ((t_f0 >= t0) & (t_f0 < t1)).any() else 0.0
    if rms_db < -45:
        cls = "silence"
    elif conf < 0.45 or med == 0:
        cls = "uncertain"
    elif med < 165:
        cls = "male"
    elif med >= 185:
        cls = "female"
    else:
        cls = "uncertain"
    rows.append([f"{t0:.1f}", f"{t1:.1f}", f"{rms_db:.1f}", f"{med:.0f}", f"{conf:.2f}", cls])

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["t0", "t1", "rms_db", "f0_med", "voiced_conf", "class"])
    w.writerows(rows)

# 合并连续同类段(≥1s 才打印,免噪声)
merged, cur = [], None
for r in rows:
    if cur and r[5] == cur[2]:
        cur[1] = r[1]
    else:
        if cur:
            merged.append(cur)
        cur = [r[0], r[1], r[5]]
merged.append(cur)
for t0, t1, c in merged:
    if float(t1) - float(t0) >= 1.0 and c != "silence":
        print(f"{float(t0):6.1f}–{float(t1):6.1f}s  {c}")
print(f"CSV={OUT} ROWS={len(rows)}")
