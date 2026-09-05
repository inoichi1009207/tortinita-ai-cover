"""飞入前比词:目标窗与供体窗(成品轴,秒)各覆盖哪些歌词行(pv/lyrics_timed.json),逐行文本必须相同且非空,否则退出码 2。
用法:python tools/lyric_window_check.py <目标起> <目标止> <供体起> <供体止>
教训(2026-09-04):两个副歌同旋律不同词——"I am yours, you are mine" vs "You and I'll be alright",飞入把词唱错了。
r4 外审后加固:参数须有限且起<止;任一窗没命中歌词行即拒(空==空不算同词);输出纯 ASCII 标记,stdout 不可编码字符降级,免得 GBK 控制台把合法窗误拦。"""
import json, sys, os, math
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
try: sys.stdout.reconfigure(errors='backslashreplace')
except Exception: pass
if len(sys.argv) != 5: print('[FAIL] need 4 args: t0 t1 d0 d1'); sys.exit(2)
try: t0, t1, d0, d1 = map(float, sys.argv[1:5])
except ValueError: print('[FAIL] args must be numbers'); sys.exit(2)
if not all(math.isfinite(x) for x in (t0, t1, d0, d1)) or not (t0 < t1 and d0 < d1): print('[FAIL] windows must be finite and start<end'); sys.exit(2)
L = json.load(open('pv/lyrics_timed.json', encoding='utf-8'))
def lines(a, b): return [o['text'] for o in L if o['t'] < b and o['t_end'] > a]
A, B = lines(t0, t1), lines(d0, d1)
print(f'target {t0}-{t1}: {A}\ndonor  {d0}-{d1}: {B}')
if not A or not B: print('[FAIL] a window covers no lyric line'); sys.exit(2)
if A != B: print('[FAIL] lyrics differ, fly-in refused'); sys.exit(2)
print('[OK] same lyrics line by line')
