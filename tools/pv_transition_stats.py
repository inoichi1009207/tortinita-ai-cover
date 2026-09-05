"""官方 PV 转场统计:读 pv/official/frames10.raw(10fps 160x90 灰度)算逐帧差分;
切点 = 差分峰;每个切点按峰宽分类:硬切(峰宽 ≤0.2s)/ 叠化(差分抬高持续 ≥0.3s);镜头内运动 = 镜头中段差分均值;切点与官方 LRC 行起点(±0.4s)的对齐率。
视频轴 = 官方 PV 轴,比官方伴奏轴早 6.594s,对齐歌词时把 LRC 时间 +6.594。"""
import numpy as np, re, os, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
FPS = 10; W, H = 160, 90
raw = np.fromfile('pv/official/frames10.raw', dtype=np.uint8); n = len(raw) // (W * H); F = raw[:n * W * H].reshape(n, H, W).astype(np.float32)
d = np.abs(np.diff(F, axis=0)).mean(axis=(1, 2))  # 帧间差分,长度 n-1;帧 k 与 k+1 之间
t = (np.arange(len(d)) + 1) / FPS
base = np.median(d); thr = max(base * 4, 6.0)
# 峰段:连续 d>thr 的区间
segs = []; k = 0
while k < len(d):
    if d[k] > thr:
        j = k
        while j < len(d) and d[j] > thr: j += 1
        segs.append((k, j)); k = j
    else: k += 1
cuts = []
for k, j in segs:
    width = (j - k) / FPS; peak = d[k:j].max()
    # 叠化:抬高持续 ≥0.3s 且峰值不极端;硬切:单帧尖峰
    kind = 'dissolve' if width >= 0.3 else 'hard'
    cuts.append((t[k], width, peak, kind))
# 排除首尾淡入淡出(前 2s / 后 3s)
dur = n / FPS
cuts = [c for c in cuts if 2 < c[0] < dur - 3]
hard = [c for c in cuts if c[3] == 'hard']; diss = [c for c in cuts if c[3] == 'dissolve']
print(f'视频 {dur:.1f}s,基线差分 {base:.2f},阈值 {thr:.1f}')
print(f'切点 {len(cuts)}:硬切 {len(hard)},叠化 {len(diss)}(叠化中位宽 {np.median([c[1] for c in diss]) if diss else 0:.2f}s)')
starts = [0.0] + [c[0] for c in cuts] + [dur]; shots = np.diff(starts)
print(f'镜头数 {len(shots)},平均镜头长 {shots.mean():.1f}s,中位 {np.median(shots):.1f}s,最短 {shots.min():.1f}s,最长 {shots.max():.1f}s')
# 镜头内运动:每镜头去掉首尾 0.5s 后的差分均值
motion = []
for a, b in zip(starts[:-1], starts[1:]):
    m = (t > a + 0.5) & (t < b - 0.5)
    if m.sum() > 3: motion.append(d[m].mean())
motion = np.array(motion); print(f'镜头内差分均值中位 {np.median(motion):.2f}(基线 {base:.2f});差分>2×基线的镜头占 {np.mean(motion > 2 * base):.0%}(=有推拉/动画的镜头)')
# 与 LRC 行起点对齐
L = []
for line in open('pv/lyrics_official.lrc', encoding='utf-8').read().split('\n'):
    m = re.match(r'\[(\d+):(\d+\.\d+)\](.+)', line)
    if m and '：' not in m.group(3) and ' : ' not in m.group(3): L.append(int(m.group(1)) * 60 + float(m.group(2)) + 6.594)
L = np.array(L); aligned = sum(1 for c in cuts if np.min(np.abs(L - c[0])) <= 0.4)
print(f'切点落在歌词行起点 ±0.4s 内:{aligned}/{len(cuts)} = {aligned/len(cuts):.0%}')
print('切点列表(视频轴 s,宽,类型):', ' '.join(f'{c[0]:.1f}{"D" if c[3]=="dissolve" else "H"}' for c in cuts))
