# 外审任务 r2:复核修订后的 `clipboard/ai-cover/TUTORIAL.md`(批 154)

你是只读审计者。上一轮(`D:/test/clipboard/ai-cover/codex-audit-tutorial-150-r1.md`,VERDICT FAIL,15 项)之后,作者按
`D:/test/clipboard/ai-cover/codex-audit-tutorial-150-disposition.md` 逐条修订了 `D:/test/clipboard/ai-cover/TUTORIAL.md`。
**只产审计文件,不改任何文件。** 出处只认你本次真读到的文件行。

## 要审什么

1. **15 项是否真的改到位**:逐项对照 r1 的建议与处置单声明,给 `已修 / 部分修 / 未修 / 改错了` 四档;处置单说「脚本不改、教程说明」的两项(150-02、150-07/08),核教程里的说明是否足以让复跑者不踩坑。
2. **修订引入的新错**:重点看 §4.6 新命令(子 shell + `$PWD/..` 路径写法在 Git Bash 下能否成立)、§7.2 新增的 `cp` 与 md5 命令、§4.2 新增的立绘/背景编号段、§4.3 新增的说话人标签段、§4.11 PV 段。
3. **敏感信息**:凭据、口令、绝对本机路径(`X:\` / `X:/`)、邮箱——有就列行号。
4. **你发现的、我没问到的重要事实**——单独一节。

代价不对称:教程一条错命令让照做者白跑几小时,误报只花作者一分钟核对 ⇒ 拿不准按「疑」报。

## 输出(写到 `D:/test/clipboard/ai-cover/codex-audit-tutorial-150-r2.md`)

首行 `VERDICT: PASS | PASS-WITH-FIXES | FAIL` + 一句理由;然后 15 项四档表(编号 | 档 | 依据行号 | 备注);新发现逐条 `[r2-NN] 位置 | 类型 | 摘句 | 问题 | 依据 | 建议`;末节「我没问到的重要事实」「无法核实」。
