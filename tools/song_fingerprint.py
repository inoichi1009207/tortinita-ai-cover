"""对 BGM/TRACK*.BGM(RIFF WAVE)扫时长/bpm/调式,找《秘密》(kokomu: 3♭ 约70bpm)候选。"""
import glob, os, sys, numpy as np, librosa
NOTES="C C# D D# E F F# G G# A A# B".split()
maj=np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88]); mnr=np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
for p in sorted(glob.glob(sys.argv[1])):
    y,sr=librosa.load(p,sr=22050,mono=True,duration=120,offset=20)
    dur=librosa.get_duration(path=p)
    if len(y)<sr*10: print(os.path.basename(p), f"{dur:.0f}s 太短"); continue
    bpm=float(librosa.feature.tempo(y=y,sr=sr)[0])
    ch=librosa.feature.chroma_cqt(y=y,sr=sr).mean(1)
    best=max(((np.corrcoef(np.roll(maj,k),ch)[0,1],f"{NOTES[k]} major") for k in range(12))|set() if False else
             [(np.corrcoef(np.roll(maj,k),ch)[0,1],f"{NOTES[k]} major") for k in range(12)]+[(np.corrcoef(np.roll(mnr,k),ch)[0,1],f"{NOTES[k]} minor") for k in range(12)])
    print(os.path.basename(p), f"{dur:.0f}s bpm={bpm:.1f} key={best[1]} r={best[0]:.2f}", flush=True)
