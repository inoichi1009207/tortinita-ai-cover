VERDICT: PASS-WITH-FIXES — 9 项中 7 项已修、2 项部分修；shell 根目录修法成立，但说话人映射总览仍残留旧链路，图片提取器也不能按 §4.11 的裸命令复建当前精选资产集。数据源：本地现行 `TUTORIAL.md`、r2 回件、r2 处置单及逐项引用的工具/素材文件。

## 审计口径

- 开工两查全绿。只读检查截至 2026-09-04；命题是 r2 指出的 9 项是否已落地，证据宇宙限于上述本地现行文件。
- 充分判据：改动在现行入口中可见、与代码一致且没有仍会误导复跑者的相反说法；残留旧说法或只能完成一半目标，判“部分修”；证据不够时按“疑”报。
- Git Bash 实测三份 shell 均通过 `bash -n`。无参 `bash -x tools/build_pitch_version.sh` 直证 `BASH_SOURCE[0]` 经 `dirname/..` 得到 `ai-cover` 根，`cygpath -m` 得到 Windows 盘符形式；三脚本盘符绝对路径检索为 0。天花板：这只覆盖 shell 语法、根目录计算和字面路径，不覆盖 RVC/ffmpeg 全链执行。

## 9 项落地表

| 编号 | 结论 | 依据行号 | 判定 |
|---|---|---|---|
| 150-07 | 已修 | `TUTORIAL.md:148`；`tools/build_pitch_version.sh:5`；`tools/fly_235.sh:3`；`tools/window_variants.sh:3` | 三份脚本都从自身位置推导根目录，并对传给 Windows 程序的文件参数使用 `ROOTW`；Git Bash 路径探针成立，盘符字面量零命中。 |
| 150-08 | 已修 | `tools/build_pitch_version.sh:5-9`；`TUTORIAL.md:148` | 先 `cd "$ROOT"`，再调用根内解释器；少于两个正常位置参数时 `$2` 为空并于耗时步骤前退出。 |
| 150-13 | 已修 | `TUTORIAL.md:247` | 坑 14 已明确写“机制未核”，括注只保留常见解释，没有再把它冒充本次已证根因。 |
| 150-14 | 已修 | `TUTORIAL.md:69,213,243` | 三处均收窄为“本次五组/这些组合没解决”，不再下“所有参数无解”的全称结论。 |
| r2-01 | 部分修 | 正确落地：`TUTORIAL.md:118`；残留：`:35,80,114`；`tools/build_voice_map.py:1-2,30-46` | §4.3 已明确映射脚本只读 ENX JSON、本地 KGO 仅场景 001 对齐；但工具表仍写 `KGO/ENX json → voice_map`，总流程仍写 `KGO→ENX`，且步骤 2 把实际“读取”弱写成“参照格式”，会继续让读者误以为脚本消费本地 KGO。 |
| r2-02 | 已修 | `TUTORIAL.md:227`；`pv/lyrics_official.lrc:8-60`；`pv/lyrics_timed.json:3-344` | 已写现行网易云 LRC、首行校准和 whisper 的历史备选地位；本地时间轴逐行标有 `src: netease-official`，除首行外起点与 LRC 对应。 |
| r2-03 | 已修 | `TUTORIAL.md:225`；`tools/build_pv3.py:18-30,54-69` | 已按现行实现写成内存 RGBA + numpy alpha 混合 + rawvideo 管道，不再写成落盘 PNG 后用 ffmpeg overlay。 |
| r2-04 | 已修 | `TUTORIAL.md:225-226` | 已把坏资产/硬编码路径所在的 `build_pv.py` 明确标为废弃，并把 `build_pv3.py` 列为现行入口，不再指示复跑旧脚本。 |
| r2-05 | 部分修 | `TUTORIAL.md:106,224`；`tools/extract_images.py:1-22` | 提取脚本已落盘，HyPack 索引字段与 §4.2 一致，能切出 comp=0 且带 PNG 签名的条目；但 §4.11 的裸命令会把 EVCG/EVBG 中所有 PNG 分别写进两个目录，不能得到教程声称“只保留”的 16 张朵朵立绘和当前精选背景，也不处理同句所列的 `SROP.MPG` 封面。 |

## shell 与提取器专项

- `bash -n`：`build_pitch_version.sh`、`fly_235.sh`、`window_variants.sh` 均为 PASS；盘符路径检索面为三文件的 `[A-Za-z]:[/\\]`，0 命中。
- 根目录：三文件的 `BASH_SOURCE[0] → dirname → .. → pwd` 写法在 Git Bash 下成立；`cygpath -m` 将 MSYS 根路径转成 Windows 原生程序可接收的盘符正斜杠路径。引用参数均有引号，根路径含空格时仍可作为单一参数。
- `extract_images.py:10-16` 与 §4.2 的 HyPack 记录布局相符：索引和正文偏移都加 `0x10`，记录步长 48，读取 name/ext/packed/comp 后按 packed 长度切片；`:19-21` 只写 comp=0、扩展名为 png、PNG 签名正确的条目。对目标封包的核心解析逻辑成立。
- 提取器天花板：`:10` 只验 `HyPack` 六字节，不验 v3 版本或索引边界；`:17-21` 不实现 §4.11 的角色白名单、精选背景或封面帧提取。因此“能解目标直存 PNG”成立，“一条命令复建当前 PV 素材集”不成立。

## 新发现

1. **[r3-01] 复跑注释与脚本相反。** `TUTORIAL.md:305` 仍说 `fly_235.sh` 不检查输入，但 `tools/fly_235.sh:4` 已检查两份输入，且教程自己在 `:148` 也说会检查。应删掉 `:305` 的旧括注。
2. **[r3-02] 图片提取范围与 §4.11 不闭合。** `TUTORIAL.md:224` 给的是只带游戏目录的命令并声称得到精选素材；`tools/extract_images.py:17-21` 实际默认提取两包中的全部 PNG，且全局单前缀过滤也无法表达 16 个离散立绘编号。应加明确白名单/模式参数，或把教程改成“先全量提取，再按清单筛选”并给筛选命令。
3. **[r3-03] 嘴型周期描述差 1 帧。** `TUTORIAL.md:225` 与 `tools/build_pv3.py:37` 写每 0.32 s 插两帧闭嘴，但代码 `:46` 为 `int(0.32 * 30) = 9` 帧，即实际每 0.30 s 一次。虽不阻断生成，现行实现描述不精确。

## 敏感信息

- 凭据/口令/API key/token/secret 的赋值：0；邮箱：0。检索面为 `TUTORIAL.md`、r2 处置单、三份 shell 与 `extract_images.py`；教程 `:4` 只出现“不含凭据”的说明。
- 绝对本机路径：目标教程和四个工具为 0；但 r2 处置单 `:9` 含一条盘符绝对路径，违反产物文件不得带绝对本机路径的卫生要求。应改成泛化的盘符路径模式或只写“盘符路径零命中”。

## 本批未覆盖

## 没问到的

1. `tools/build_pitch_version.sh:6` 只验证 `$2` 非空；显式传空标签、合法半音时仍会继续并生成无标签文件名。正常少传参数会拦住，但若要让“缺参数即退出”字面完全成立，应同时验证 `$1` 并校验 `$2` 为数值。
2. 当前 `pv/assets/sprites/` 恰为 16 张、`pv/assets/bg/` 为 10 张精选文件；这反证它们不是 `extract_images.py <游戏目录>` 默认全量输出本身，教程缺了中间筛选步骤。

## 无法核实

1. 按任务要求没有读取或运行游戏目录，故未实测目标 `EVCG.PAK`/`EVBG.PAK` 的实际条目数、路径层级和全量输出；对提取器的判断限于代码与教程所载 HyPack 布局。
2. 没有执行 RVC、ffmpeg 或三份 shell 的音频全链；`bash -n` 和路径探针抓不到依赖缺失、素材缺失及运行期媒体错误。
3. 本机 `python` 不在 PATH，仓内 `venv` 启动器所指基础解释器也不存在，因此没有执行 Python 语法/最小封包探针；`extract_images.py` 结论是逐行静态审读。
4. 没有联网重取网易云接口，也没有重做四处人声包络校准；r2-02 只核到仓内 LRC、JSON 与现行教程互相一致。
