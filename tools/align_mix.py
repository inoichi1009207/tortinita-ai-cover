"""对齐并混音:用「自分离伴奏(与人声同时间轴)」与「官方伴奏」做起始偏移互相关,
   把该偏移应用到转换后人声,与官方伴奏混合出成品。"""
import numpy as np, librosa, subprocess, sys

AI = r"D:\test\clipboard\ai-cover"
OFF_INST = AI + r"\official\goodbye_instrumental_official.mp3"
SEP_INST = AI + r"\stems-gpu\goodbye_src_(Instrumental)_model_bs_roformer_ep_317_sdr_12.flac"
VOCAL = AI + r"\torta_lead_full.wav"
OUT_FLAC = AI + r"\goodbye_torta_v1.flac"
OUT_MP3 = AI + r"\goodbye_torta_v1.mp3"

SR = 22050
a, _ = librosa.load(OFF_INST, sr=SR, mono=True, duration=60)
b, _ = librosa.load(SEP_INST, sr=SR, mono=True, duration=60)
oa = librosa.onset.onset_strength(y=a, sr=SR)
ob = librosa.onset.onset_strength(y=b, sr=SR)
n = min(len(oa), len(ob))
oa, ob = oa[:n] - oa[:n].mean(), ob[:n] - ob[:n].mean()
xc = np.correlate(ob, oa, mode="full")
lag_frames = int(np.argmax(xc)) - (n - 1)
hop = 512
lag_sec = lag_frames * hop / SR  # >0: 分离伴奏(=人声轴)比官方晚出现 lag 秒 ⇒ 人声须提前 lag
print(f"LAG_FRAMES={lag_frames} LAG_SEC={lag_sec:+.3f} PEAK={xc.max():.1f} MEDIAN={np.median(np.abs(xc)):.1f}")

# 人声对齐:lag>0 ⇒ 掐掉人声开头 lag 秒;lag<0 ⇒ 人声前面垫静音
if lag_sec >= 0:
    v_filter = f"atrim=start={lag_sec:.3f},asetpts=PTS-STARTPTS"
else:
    ms = int(-lag_sec * 1000)
    v_filter = f"adelay={ms}|{ms}"

cmd = ["ffmpeg", "-y", "-loglevel", "error",
       "-i", VOCAL, "-i", OFF_INST,
       "-filter_complex",
       f"[0:a]{v_filter},aresample=44100[v];"
       f"[1:a]aresample=44100[i];"
       f"[v][i]amix=inputs=2:duration=shortest:normalize=0[m];"
       f"[m]alimiter=limit=0.98[out]",
       "-map", "[out]", "-c:a", "flac", OUT_FLAC]
r = subprocess.run(cmd, capture_output=True)
print("FLAC_EXIT", r.returncode, r.stderr.decode(errors="replace")[-200:] if r.returncode else "")
r2 = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", OUT_FLAC,
                     "-c:a", "libmp3lame", "-b:a", "320k", OUT_MP3], capture_output=True)
print("MP3_EXIT", r2.returncode)
