"""把参考歌词行(pv/lyrics_raw.txt)对齐到 whisper 逐词时间戳(pv/whisper_words.json),输出 pv/lyrics_timed.json + pv/lyrics.lrc(成品轴)。
方法:两边词序列做 difflib 匹配;每行的起止 = 该行匹配到的第一个/最后一个词的时间;没匹配到词的行按前后行内插并标 est=true。"""
import json, re, difflib, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
norm = lambda w: re.sub(r"[^a-z']", '', w.lower())
ref_lines = [l for l in open('pv/lyrics_raw.txt', encoding='utf-8').read().split('\n') if l.strip()]
ref_words = []  # (行号, 词)
for i, l in enumerate(ref_lines):
    for w in l.split():
        if norm(w): ref_words.append((i, norm(w)))
W = json.load(open('pv/whisper_words.json', encoding='utf-8'))['words']
hyp = [norm(w['w']) for w in W]
sm = difflib.SequenceMatcher(a=[w for _, w in ref_words], b=hyp, autojunk=False)
line_t = {}
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag in ('equal', 'replace'):
        for k in range(min(i2 - i1, j2 - j1)):
            li = ref_words[i1 + k][0]; w = W[j1 + k]
            s, e = line_t.get(li, (1e9, -1e9)); line_t[li] = (min(s, w['t']), max(e, w['t_end']))
matched = sum(1 for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag == 'equal' for _ in range(i2 - i1))
print(f'参考词 {len(ref_words)} / whisper 词 {len(hyp)} / 完全匹配词 {matched} ({matched/len(ref_words):.0%})')
out = []
for i, l in enumerate(ref_lines):
    if i in line_t: s, e = line_t[i]; out.append({'i': i, 'text': l, 't': round(s, 2), 't_end': round(e, 2), 'est': False})
    else: out.append({'i': i, 'text': l, 't': None, 't_end': None, 'est': True})
# 内插缺失行
for k, o in enumerate(out):
    if o['t'] is None:
        prev = next((x for x in reversed(out[:k]) if x['t'] is not None), None); nxt = next((x for x in out[k + 1:] if x['t'] is not None), None)
        if prev and nxt: o['t'] = round(prev['t_end'] + 0.3, 2); o['t_end'] = round(max(o['t'] + 1.5, nxt['t'] - 0.3), 2)
        elif prev: o['t'] = round(prev['t_end'] + 0.3, 2); o['t_end'] = o['t'] + 3
        elif nxt: o['t_end'] = round(nxt['t'] - 0.3, 2); o['t'] = max(0, o['t_end'] - 3)
# 行尾至少延到下一行开始前 0.15s,避免闪
for k in range(len(out) - 1):
    out[k]['t_end'] = max(out[k]['t_end'], min(out[k + 1]['t'] - 0.15, out[k]['t_end'] + 2.0))
json.dump(out, open('pv/lyrics_timed.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
with open('pv/lyrics.lrc', 'w', encoding='utf-8') as f:
    for o in out: m, s = divmod(o['t'], 60); f.write(f'[{int(m):02d}:{s:05.2f}]{o["text"]}\n')
for o in out: print(f"{o['t']:7.2f}-{o['t_end']:7.2f} {'~' if o['est'] else ' '} {o['text']}")
