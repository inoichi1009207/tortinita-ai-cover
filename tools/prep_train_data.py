"""按 voice_map 圈 Torta/Chris 语料,ffmpeg 转 16bit PCM 44.1kHz mono 到 dataset/train/<spk>/。
   剔除唯一归属冲突条 93169。文件定位规则:raw/SREV{id前3位}_{id补6位}.wav(跨场景引用照此)。"""
import csv, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

BASE = r"D:\test\clipboard\ai-cover\dataset"
RAW, OUT = os.path.join(BASE, "raw"), os.path.join(BASE, "train")
SPEAKERS = {"Torta": "torta", "Chris": "chris"}
EXCLUDE = {"93169"}

jobs = []
seen = set()
with open(os.path.join(BASE, "voice_map.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        sp, vid = r["speaker"], r["voice_id"]
        if sp not in SPEAKERS or vid in EXCLUDE or vid in seen:
            continue
        seen.add(vid)
        v6 = vid.zfill(6)
        src = os.path.join(RAW, f"SREV{v6[:3]}_{v6}.wav")
        dst = os.path.join(OUT, SPEAKERS[sp], f"{v6}.wav")
        jobs.append((src, dst))

for d in SPEAKERS.values():
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

def conv(t):
    src, dst = t
    if not os.path.exists(src):
        return ("MISS", src)
    p = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src,
                        "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1", dst],
                       capture_output=True)
    return ("OK", dst) if p.returncode == 0 else ("FAIL", src + " :: " + p.stderr.decode(errors="replace")[:120])

with ThreadPoolExecutor(max_workers=8) as ex:
    res = list(ex.map(conv, jobs))

ok = sum(1 for s, _ in res if s == "OK")
bad = [(s, m) for s, m in res if s != "OK"]
for s, m in bad[:10]:
    print(s, m, file=sys.stderr)
per = {}
for _, dst in [r for r in res if r[0] == "OK"]:
    k = os.path.basename(os.path.dirname(dst))
    per[k] = per.get(k, 0) + 1
print(f"TOTAL_JOBS={len(jobs)} OK={ok} BAD={len(bad)} PER={per}")
