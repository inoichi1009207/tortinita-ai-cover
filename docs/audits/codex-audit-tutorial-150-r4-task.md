# 外审任务 r4(增量):`clipboard/ai-cover/TUTORIAL.md` 本批新增的 v3b 段 + `tools/lyric_window_check.py`

你是只读审计者,只审**本批新增/改动**的部分(其余已经 r1–r3 三轮):
1. `D:/test/clipboard/ai-cover/TUTORIAL.md` §0 里以「**v3b(2026-09-04)修正一个 v3 的硬伤**」开头的一段:时间数值(154.0–157.2 ← 69.32–72.52、157.3–162.0、互相关 1.000/−0.100)是否与 `tools/fly_235.sh`、`tools/fly_107.sh` 里的常数一致(源轴 = 成品轴 + 6.594);「教训」一句是否过强。
2. `D:/test/clipboard/ai-cover/tools/lyric_window_check.py` 与它在两份 fly 脚本里的挂载:逻辑能否按字面拦住「同旋律不同词」;`|| exit 2` 在 `set -e` 下是否成立;有无路径/编码坑。
3. 敏感信息(凭据、绝对本机路径、邮箱)。
4. 你发现的、我没问到的——单独一节。
只产审计文件,不改任何文件。拿不准按「疑」报。

输出到 `D:/test/clipboard/ai-cover/codex-audit-tutorial-150-r4.md`:首行 `VERDICT: PASS | PASS-WITH-FIXES | FAIL` + 一句理由;逐条 `[r4-NN] 位置 | 类型 | 摘句 | 问题 | 依据 | 建议`;末节「没问到的」「无法核实」。
