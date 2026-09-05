"""HyPack v3 VOICE 提取器(交响乐之雨,规格=GARbro ArcKogado.cs,codex 外审钉过的坑已含:
   索引基址 +0x10、按 SREV*.PAK 通配枚举、逐条读采样率不假定 44.1k)。
   只读游戏目录,产物写 clipboard/ai-cover/dataset/raw/ + stats.csv。"""
import csv, glob, os, struct, sys

GAME = r"D:\znsy\交响乐之雨\交响乐之雨"
OUT = r"D:\test\clipboard\ai-cover\dataset\raw"
CSV = r"D:\test\clipboard\ai-cover\dataset\stats.csv"

def parse_wav_meta(buf):
    """从 RIFF 里取 (sample_rate, duration_sec)。MS-ADPCM 时长优先用 fact 块样本数。"""
    if buf[:4] != b"RIFF" or buf[8:12] != b"WAVE":
        return None, None
    pos, rate, samples, data_len, block_align, spb = 12, None, None, None, None, None
    while pos + 8 <= len(buf):
        cid, clen = buf[pos:pos+4], struct.unpack_from("<I", buf, pos+4)[0]
        body = pos + 8
        if cid == b"fmt ":
            rate = struct.unpack_from("<I", buf, body+4)[0]
            block_align = struct.unpack_from("<H", buf, body+12)[0]
            if clen >= 20:  # MS-ADPCM 扩展域:samplesPerBlock
                spb = struct.unpack_from("<H", buf, body+18)[0]
        elif cid == b"fact":
            samples = struct.unpack_from("<I", buf, body)[0]
        elif cid == b"data":
            data_len = clen
        pos = body + clen + (clen & 1)
    if rate is None:
        return None, None
    if samples:
        return rate, samples / rate
    if data_len and block_align and spb:
        return rate, (data_len / block_align) * spb / rate
    return rate, None

def main():
    os.makedirs(OUT, exist_ok=True)
    paks = sorted(glob.glob(os.path.join(GAME, "VOICE", "SREV*.PAK")))
    rows, total = [], 0
    for pak in paks:
        base = os.path.splitext(os.path.basename(pak))[0]
        with open(pak, "rb") as f:
            data = f.read()
        assert data[:6] == b"HyPack", pak
        idx = 0x10 + struct.unpack_from("<I", data, 8)[0]
        count = struct.unpack_from("<I", data, 12)[0]
        for i in range(count):
            rec = idx + 48 * i
            name = data[rec:rec+0x15].split(b"\0")[0].decode("ascii")
            ext = data[rec+0x15:rec+0x18].split(b"\0")[0].decode("ascii")
            off = 0x10 + struct.unpack_from("<I", data, rec+0x18)[0]
            unpacked = struct.unpack_from("<I", data, rec+0x1c)[0]
            packed = struct.unpack_from("<I", data, rec+0x20)[0]
            comp = data[rec+0x24]
            if comp != 0:
                print(f"SKIP 非直存条目 {base}/{name} comp={comp}", file=sys.stderr)
                continue
            body = data[off:off+packed]
            rate, dur = parse_wav_meta(body)
            fn = f"{base}_{name}.{ext}"
            with open(os.path.join(OUT, fn), "wb") as w:
                w.write(body)
            rows.append([base, name, rate, packed, f"{dur:.3f}" if dur else ""])
            total += 1
    with open(CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pak", "entry", "sample_rate", "bytes", "seconds"])
        w.writerows(rows)
    durs = [float(r[4]) for r in rows if r[4]]
    rates = {}
    for r in rows:
        rates[r[2]] = rates.get(r[2], 0) + 1
    print(f"EXTRACTED={total} PAKS={len(paks)} CSV_ROWS={len(rows)}")
    print(f"RATES={rates}")
    print(f"TOTAL_HOURS={sum(durs)/3600:.2f} MEAN_SEC={sum(durs)/len(durs):.2f}" if durs else "NO_DURATION")

if __name__ == "__main__":
    main()
