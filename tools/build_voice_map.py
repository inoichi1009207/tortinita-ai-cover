"""从 SymphonicRain-ENX 的反汇编 json 建「语音 id → 说话人」映射。
   Voice(U32=id) 后最近一条 Text 的 [Name] 前缀 = 说话人。
   产物: dataset/voice_map.csv + 按角色聚合统计(联 stats.csv 时长)。"""
import csv, json, os, re, urllib.request

TOOLS = r"D:\test\clipboard\ai-cover\tools\enx_jsons"
OUT = r"D:\test\clipboard\ai-cover\dataset\voice_map.csv"
STATS = r"D:\test\clipboard\ai-cover\dataset\stats.csv"
RAW = "https://raw.githubusercontent.com/masagrator/SymphonicRain-ENX/main/jsons/scr%04d.json"

os.makedirs(TOOLS, exist_ok=True)

def fetch_all():
    got, miss = 0, []
    for n in range(1, 200):
        p = os.path.join(TOOLS, "scr%04d.json" % n)
        if os.path.exists(p):
            got += 1
            continue
        try:
            urllib.request.urlretrieve(RAW % n, p)
            got += 1
        except Exception:
            miss.append(n)
    return got, miss

def build():
    rows = []
    tag_re = re.compile(r"^\s*\[([^\]]+)\]")
    for fn in sorted(os.listdir(TOOLS)):
        if not fn.endswith(".json"):
            continue
        scene = fn[3:7]
        d = json.load(open(os.path.join(TOOLS, fn), encoding="utf-8"))
        flat = [e for f in d["COMMANDS"] for e in f]
        for i, e in enumerate(flat):
            if e.get("TYPE") != "Voice" or "U32" not in e:
                continue
            vid = e["U32"][0]
            speaker = ""
            for j in range(i + 1, min(i + 6, len(flat))):
                if flat[j].get("TYPE") == "Text":
                    m = tag_re.match(flat[j]["STRING"][0]) if flat[j].get("STRING") else None
                    speaker = m.group(1) if m else "(无标签)"
                    break
            rows.append([scene, vid, speaker])
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scene", "voice_id", "speaker"])
        w.writerows(rows)
    return rows

def aggregate(rows):
    dur = {}
    with open(STATS, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            # entry 如 001001;voice_id 是 int(去前导零)
            dur[int(r["entry"])] = float(r["seconds"] or 0)
    agg, matched = {}, 0
    for scene, vid, sp in rows:
        d = dur.get(vid)
        if d is not None:
            matched += 1
            a = agg.setdefault(sp, [0, 0.0])
            a[0] += 1
            a[1] += d
    return agg, matched

if __name__ == "__main__":
    got, miss = fetch_all()
    print(f"JSONS={got} MISS={miss[:10]}{'...' if len(miss)>10 else ''}")
    rows = build()
    print(f"VOICE_CMDS={len(rows)}")
    agg, matched = aggregate(rows)
    print(f"MATCHED_TO_WAV={matched}")
    for sp, (n, sec) in sorted(agg.items(), key=lambda x: -x[1][1]):
        print(f"{sp}\t{n} 条\t{sec/60:.1f} 分钟")
