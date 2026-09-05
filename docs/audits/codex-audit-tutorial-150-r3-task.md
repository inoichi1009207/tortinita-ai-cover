# 外审任务 r3:核 r2 修订是否落地——`clipboard/ai-cover/TUTORIAL.md` 与 `clipboard/ai-cover/codex-audit-tutorial-150-r2-disposition.md`

你是只读审计者。r2 回件(`D:/test/clipboard/ai-cover/codex-audit-tutorial-150-r2.md`)之后,作者按处置单
`D:/test/clipboard/ai-cover/codex-audit-tutorial-150-r2-disposition.md` 改了 `D:/test/clipboard/ai-cover/TUTORIAL.md` 与三份 shell 工具
(`tools/build_pitch_version.sh`、`tools/fly_235.sh`、`tools/window_variants.sh`),并新增 `tools/extract_images.py`。**只产审计文件,不改任何文件。**

## 要审什么(短平快)

1. r2 的 4 项「部分修」(150-07/08/13/14)与 5 项新发现(r2-01…05)是否**真的落地**:逐项给 `已修 / 部分修 / 未修 / 改错了`,附行号。
2. 三份 shell 工具的根目录推导:`ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"` + `cygpath -m` 在 Git Bash 下是否成立;`bash -n` 三份;`grep` 盘符路径应为零。
3. `tools/extract_images.py` 是否能按教程 §4.2/§4.11 的描述工作(只看代码逻辑与 HyPack 索引解析,不跑游戏目录)。
4. 敏感信息:凭据、口令、绝对本机路径、邮箱。
5. 你发现的、我没问到的——单独一节。

代价不对称同前:教程错命令让人白跑几小时,误报只花一分钟核 ⇒ 拿不准按「疑」报。

## 输出(写到 `D:/test/clipboard/ai-cover/codex-audit-tutorial-150-r3.md`)

首行 `VERDICT: PASS | PASS-WITH-FIXES | FAIL` + 一句理由;9 项落地表;新发现逐条;末节「没问到的」「无法核实」。
