# 朵鲁妲 AI 翻唱《相别 Goodbye》—— 工具与教程

用《交响乐之雨》(工画堂,2004)里朵鲁妲(トルティニタ,CV 中原麻衣)的游戏语音自训 RVC 声库,
翻唱《重返未来:1999》的《相别 Goodbye》,并做了一支带雨效与歌词的 PV。**个人爱好项目,非官方。**

PV 已上传至 [bilibili](https://www.bilibili.com/video/BV1v2ty6oEsv/)，欢迎来看。

## 为什么做

通完《交响乐之雨》的 al fine 后,作者脑子里忽然响起了《相别 Goodbye》。
于是就有了一个很简单的目标:作者想听朵鲁妲把它唱出来。

最开始只是想训一个声库做 AI 翻唱,最后一路踩到了游戏解包、说话人映射、
RVC、多声部分离、局部音频修补、混音和 PV。这个仓库就是整个过程留下来的工具和记录。

## 怎么看这个仓库

这是一次「人做取舍,Agent 做工程」的个人实验。

整个制作过程主要由 Claude Code / Codex 协助完成:它们负责游戏文件侦察、脚本编写、
模型训练与推理、音频分析、批量实验、PV 工具和文档整理;作者负责确定目标、提供合法素材、
逐版试听、判断哪些结果能用,以及最后的音乐和画面取舍。

所以这里的脚本不要求你逐行手敲,也不要求你必须使用和作者相同的 Agent。
如果你只是想复现一次 AI 翻唱,可以把本 README 和 `tools/` 交给你自己的 Coding Agent,
让它先读懂流程,再根据你的操作系统、游戏目录和目标角色改造。

当然,README 本身也是给人看的:从下面的「一句话结果」和「总流程」开始,
不用 Agent 也能看懂这次到底做了什么、为什么这样做,以及作者踩过哪些坑。

> **给 Coding Agent:** 先完整阅读 README,尤其是 §4、§5 和 §7;
> 不要直接照抄本机路径或版本号。先检查当前环境、依赖版本和输入素材,再决定哪些脚本可以复用。

## 一句话结果

朵鲁妲唱了《相别 Goodbye》,整首比原唱低两个半音。

她的声音是从游戏里 1,739 句对白训出来的。歌是官方版本:人声换成了她的声音,伴奏还是官方的。
原唱有两处主唱与和声关系比较复杂,直接做 RVC 会出问题,所以从另一段副歌移植了可用的同词片段,再单独处理和声。
PV 是游戏里的场景加了雨,雨只下在窗户外面。

细节、参数和几十个失败版本,都在下面的教程里。

## 这里没有什么

- **游戏文件**:封包、背景图、语音、OP 视频都不在仓里。脚本里的文件名(`SROP.MPG`、`srbg054.png`……)照原样保留,复现请用自己的游戏副本。
- **训练出来的声库**:语料来自商业游戏的配音,声库本身只在本地使用,不随本仓发布;教程给的是完整的复现路径。
- **音频成品、数据集、分离出来的音轨、渲染出来的视频、歌词文本文件、虚拟环境**:见 `.gitignore`。

## 目录

本仓存的是**整条流水线的脚本与文字记录**:游戏封包侦察与语音提取、说话人映射、Applio 训练、
两级干声分离、RVC 推理、对齐与混音、两处病灶的「飞入」修补、音高取舍、PV 合成。

- `tools/` —— 全部脚本(Python / shell / C# / Node)。四份 shell 工具按脚本位置推导根目录;
  早期 Python 脚本、两份 Node 训练驱动(`train-*-driver.mjs`)与 `whisper_words.py` 的模型目录
  写死着作者本机路径(`D:\test\clipboard\ai-cover`、游戏目录、`D:/hf-home`),改顶部那几行常量即可。
  - `GARbro_AudioADP.cs` 摘自 [GARbro](https://github.com/morkt/GARbro)(MIT,morkt),`Adp1Decode.cs` 是据它写的独立命令行移植。
    `KogadoCocotte.cs` 同样取自 GARbro,但它是 juicy.gt 的 **GPL v2** 代码的 C# 移植(内含 Michael Schindler 的 range coder),
    `ExtractScript.cs` 依赖它,同属 GPL v2 派生件。编译产物 `.exe` 不入仓。
  - `kgo_commands.py` / `kgo_assembler.py` 来自 [SymphonicRain-ENX](https://github.com/masagrator/SymphonicRain-ENX)(本项目只把它们当只读参考;上游未声明许可证)。
  - 本仓采用 MIT;上面这几份第三方文件不在 MIT 之内,各自的条款见 `LICENSE` 末尾的例外条款。
  - `rain_v2.py`、`build_pv9_rain_v2.py`、`build_pv9_rain_v2.patch` 是让 codex(gpt-6-astra)试做雨效时的产物,
    留档对照,**最终 PV 没有采用**(它手标的掩膜比游戏背景自带的 alpha 通道保守得多,见教程 4.11)。
- `README.md` —— 本文,下面从「全流程教程」起是完整教程(经 codex 四轮只读外审;审计记录不入仓)。

---

# 朵鲁妲 AI 翻唱《相别 Goodbye》全流程教程

> 从游戏目录里挖语料、训一个 RVC 声库,到把一首歌调到能听——工具、步骤、原理、流程、踩过的坑,全部按实际发生的顺序写。
> 只写这次真做过、真测到的事;拿不准的地方标「未核实」。本文不含任何凭据;路径一律相对 `clipboard/ai-cover/`,游戏目录写作 `<游戏目录>`。
> 性质:个人爱好。成品发布须标「AI 翻唱 · 非官方」。

---

## 0. 一句话结果

用《交响乐之雨》里朵鲁妲(トルティニタ,CV 中原麻衣)的 **1,739 句对白(138 分钟)** 训了一个 RVC 声库(Applio,130 轮),
把《重返未来:1999》的《相别 Goodbye》官方主唱干声转成她的声音,最终成品 = **全曲降 2 半音**(人声 RVC 重转 + 官方伴奏 rubberband 移调)
+ **两处 flying-in 移植**(1:01–1:07 与 2:34–2:41,同曲另一副歌的同词段飞入)+ **两处官方和声复活窗**(主唱 −1.5 dB / 伴奏 +2 dB)。
中间版 v3(2026-09-04 下午,已被下面的最终版取代):`goodbye_torta_final_v3.mp3` = v4a 混音链(伴奏 250 Hz −2 dB + 主唱触发的 2:1 侧链让位,整体对齐 −12 LUFS)+ 2:34 飞入 + **1:07 "Memories of time" 再飞入**(`tools/fly_107.sh`:第二副歌 150.13–153.88 → 65.45–69.20,偏移 84.68 s 由两窗包络互相关测得,入/出点都放在 weave|Me、time|Stitching 之间的能量低谷;第一刀切在 65.7 s,落在 Me 起音 65.6 s 之后,出了 "Mememory"——飞入的刀口必须量起音、不能按歌词表时间估)+ 去掉 memory 窗的旧自动化。旧定稿 v2 = `goodbye_torta_fullB_FLYHARM235.mp3` 加标签,已被替代。
**v3b(2026-09-04)修正一个 v3 的硬伤**:2:34 的飞入窗原来是 154.0–160.6 s,把第一副歌的 "Stitching / I am yours, you are mine" 整段盖到了第二副歌的 "Stitching / You and I'll be alright" 上——两个副歌**歌词不同**,作者听出唱错词。现在只飞 Stitching(154.0–157.2 ← 69.32–72.52,刀口在 157.2 s 的能量低谷),"You and I'll be alright" 保留原第二副歌主唱,并把和声复活窗移到它身上(157.3–162.0)。核对用互相关:157.3–162.0 新主唱与原第二副歌 1.000、与第一副歌对应段 −0.100。**教训:飞入前先逐句比两段歌词,同旋律不等于同词。** 已固化为 `tools/lyric_window_check.py`:两份 fly 脚本在剪接前用**同一组**成品轴窗口变量调用它,任一窗没命中歌词行或逐行文本不同即退出 2(codex r4 外审后加固:空窗不放行、参数校验、纯 ASCII 输出免得 GBK 控制台把合法窗误拦)。
**最终版(2026-09-04 晚,B 站投稿用的就是它)= `goodbye_torta_final_20260904b.mp3`**:`goodbye_torta_final_20260904.mp3`(= v3b 同流,音频与 `goodbye_torta_final_v4a_FLY107_NOHARM.mp3` 逐位相同)之上只把 2:26.5–2:40.5 的官方和声压 −6 dB(用 karaoke 模型把官方伴奏拆成和声轨与纯伴奏,`tools/harmony_mix.py` 窗口模式),窗口外逐样本不变;1:0x 段按作者裁定不压。

---

## 1. 工具清单

| 工具 | 用途 | 来源 / 版本 | 用在哪一步 |
|---|---|---|---|
| BBDown | 下载 B 站官方 PV 的音轨 | winget 安装,扫码登录一次 | §4.1 素材 |
| ffmpeg / ffprobe | 切、拼、混音、移调(rubberband 滤镜)、转码、测时长 | 系统 PATH | 全程 |
| audio-separator(python-audio-separator) | 干声分离 | `venv-train`;模型 `model_bs_roformer_ep_317_sdr_12.9755.ckpt`、`mel_band_roformer_karaoke_aufr33_viperx_sdr_10` | §4.5 分离、§4.9 游戏歌曲分离 |
| Applio(RVC 分支) | 预处理 / 特征提取 / 训练 / 推理 | `venv-applio`,torch 2.11.0+cu130;嵌入器 contentvec;F0 法 rmvpe / crepe / fcpe | §4.4 训练、§4.6 推理 |
| torch(训练侧) | GPU 计算 | `venv-train`:torch 2.13+cu130,onnxruntime-gpu | §4.4、§4.5 |
| librosa | pyin 测 F0、色度、节拍、谱平坦度、HPSS、MFCC/DTW | `venv` | 全部「量」的步骤 |
| rubberband(ffmpeg 内置滤镜) | 伴奏移调;人声移调(**实测不可用**,见坑 14) | ffmpeg | §4.8 |
| pedalboard | 混响(v2b/v3b 试过,定稿是干版) | `venv-applio` | §4.7 |
| GARbro 源码 | 封包与音频格式规格:`ArcKogado.cs`(HyPack)、`KogadoCocotte.cs`(Cocotte 解压)、`Hypatia/AudioADP.cs`(ADP1) | GitHub morkt/GARbro,只读源码 | §4.2、§4.9 |
| csc(.NET Framework 4.8 自带 C# 5 编译器) | 编译 `KogadoCocotte.cs` 移植件与 `Adp1Decode.cs` | 系统自带 | §4.2、§4.9 |
| SymphonicRain-ENX(GitHub masagrator) | KGO 脚本反汇编格式参考 → 说话人映射 | 只读参考 | §4.3 |
| `tools/extract_voice.py` | 从 `VOICE/SREV*.PAK` 提取 WAV,记 `dataset/stats.csv` | 自写 | §4.2 |
| `tools/ExtractScript.cs` + `tools/KogadoCocotte.cs` | 解 `SCRIPT.PAK` 的 Cocotte 压缩,吐出 KGO | 自写 + GARbro 移植 | §4.3 |
| `tools/build_voice_map.py` | 读 SymphonicRain-ENX 反汇编 json → `dataset/voice_map.csv`(语音 id → 说话人);不读本地 KGO | 自写 | §4.3 |
| `tools/prep_train_data.py` | 按说话人分拣、转 ASCII 文件名、落 `dataset/train/<角色>/` | 自写 | §4.3 |
| `tools/export_weight.py` | 从 `G_*.pth` 检查点导出推理权重 `.pth` | 自写 | §4.4 |
| `tools/align_mix.py` | 互相关对齐 + 混音(早期版本用) | 自写 | §4.7 |
| `tools/harmony_route_map.py` | 和声路线台账(和声怎么处理的记录) | 自写 | §4.10 |
| `tools/Adp1Decode.cs` → `tools/Adp1Decode.exe` | `SONG/SRxx/SONG.ADP`(ADP1 4-bit ADPCM)→ WAV | GARbro 逻辑移植 | §4.9 |
| `tools/f0_range.py` | 测一段音频的音域 P10 / 中位 / P90 | 自写 | §4.8 |
| `tools/adp1_probe.py` | 试探 ADPCM 声道排布(低/高半字节) | 自写 | §4.9 |
| `tools/song_fingerprint.py`、`tools/bgm_fingerprint.py` | 批量测 bpm / 调式找目标曲 | 自写 | §4.9 |
| `tools/build_pitch_version.sh` | 一条命令出「整曲降 N 半音」版本 | 自写 | §4.8 |
| `tools/window_variants.sh` | 只重转一个窗口、扫 RVC 参数、拼回、切片 | 自写 | §4.10 |
| `tools/fly_235.sh` | 2:34–2:41 的 flying-in + 和声复活三版 | 自写 | §4.10 |

三个虚拟环境为什么分开:训练侧、Applio 推理侧、分析侧的 torch/onnxruntime 版本互相打架,且**运行中的进程锁着 DLL,强制重装会失败**(坑 7)。分开最省事。

---

## 2. 原理(给没做过的人)

**SVC(歌声转换)是什么。** 输入是一段真人唱的干声,输出是「同一段演唱,换成另一个人的嗓子」。它保留输入的音高走向、节奏、咬字,只替换音色。
所以**不需要歌词文本,也不需要 MIDI**:旋律和时值全从输入干声里来。这和 TTS / 歌声合成(需要谱)是两回事。

**预训练底模 + 微调。** RVC 的底模在海量多说话人数据上学会了「从内容特征 + 音高 → 波形」这件事;微调只用目标人物的几十分钟到几小时数据,把「音色」那部分拧过去。
所以 138 分钟对白就够了。**本次实测:日语对白语料训出的模型能唱这首英文歌**;通常解释是内容特征(contentvec)有一定跨语种迁移能力、音色与内容在模型里分开表示——这个机制本文没有做消融或对照核实,只是经验性说法。

**推理时几个参数各管什么(Applio 名称)。**
- `--pitch N`:把输入 F0 整体乘 2^(N/12) 再喂给模型。−2 = 降大二度。
- `--f0-method`:F0 提取器。rmvpe 稳;crepe 慢而细;fcpe 快。单声部干声三者差不多,**多声部输入三者全部乱飞**(见下)。
- `--index-rate`:检索特征库(`.index`)的混入比例。高 → 更像训练集音色,但输入若与训练集差得远会「拉扯」;低 → 更贴输入。本次 0.6 为主,窗口扫描试过 0.3 / 0.85。
- `--protect`:保护清辅音与气声不被模型「唱化」。0.35 默认,0.5 更保守。
- `--formant-shifting --formant-timbre 0.88`:只动共振峰不动音高——听感变「厚」但音区不变。

**干 / 湿 与 LUFS。** 干 = 无混响的原始声;湿 = 加了空间感。LUFS 是响度单位(按人耳感知加权的能量),用来比较「这版是不是比那版更响」,而不是看峰值。游戏对白语料是很干的录音,所以模型出来也干;定稿没加混响。

**为什么多声部进 RVC 会 F0 乱飞。** F0 提取器假设一次只有一条基频。两条以上同时唱(主唱 + 和声),它会在两条之间跳,本次实测 F0 逐帧标准差 160–180 音分(单声部段落的读数明显更低,具体值本文未留表)。模型跟着这条抖动的 F0 唱,听感就是「asasasas」式的颤抖或碾碎。本次 rmvpe/crepe/fcpe 与 index/protect 五组扫描都没解决,最终靠换输入(见 §4.10)。

**为什么 rubberband 移调人声会「空灵」。** 本文只坐实了现象:v23 人声经 rubberband 移 −2(B2 版)全曲空灵,作者一耳朵否掉;伴奏走同一滤镜听不出本质差别(B3 对照)。机制上通常归于相位声码器类算法对谐波相位/瞬态的处理,本文没有做相位测量,**未核**。工艺结论不变:人声只走 RVC `--pitch`,伴奏才用 rubberband。

---

## 3. 总流程(先看地图)

```
素材 ──► 官方 PV 音轨(BBDown) ──► 两级分离 ──► 主唱干声 + 和声轨
                                              │
游戏目录 ──► HyPack 解包 ──► VOICE WAV ──► 说话人映射(ENX 反汇编 json 的 [Name])──► 朵朵语料 ──► Applio 训练 ──► torta.pth + torta.index
                                              │                                            │
                                              └──────────► RVC 推理(pitch / f0 / index / protect)◄─┘
                                                                     │
官方伴奏(作者提供的链接 → ffmpeg 转码) ──────────────────────────────┤
                                                                     ▼
                                    对齐(+6.594 s)──► 混音配方 ──► 逐版耳裁 ──► 病灶定位(逐秒量)──► flying-in / 和声复活 ──► 定稿
```

---

## 4. 分步流程

### 4.1 素材:官方主唱与官方伴奏

- **官方 PV 音轨**:BBDown 下 B 站官方视频得到 `.m4a`。坑:中文文件名 + m4a 直接喂分离器会「Format not recognised」,先 `ffmpeg -i <m4a> -ar 44100 goodbye_src.wav` 转成 ASCII 文件名的 WAV。
- **官方伴奏**:作者给了网易云 CDN 直链,下下来转成 `official/goodbye_instrumental_official.mp3`。**它里面已经包含全部和声**(男声、女声和声都被官方定性为伴奏的一部分)。这是后面「和声复活」这招能成立的前提。
- **时间轴常数**:视频音轨比官方伴奏**早 6.594 s**(互相关测得)。所以任何从视频侧提出来的人声,混进官方伴奏前都要 `atrim=start=6.594`。
- 核对:`ffprobe` 时长、`ffmpeg -f md5` 比对流哈希。

### 4.2 游戏目录侦察与语音提取

只读游戏目录,产物全落 `dataset/`。

- **封包格式 HyPack v3**:文件头 `HyPack\0\3`;`u32@8` = 索引相对 `0x10` 的偏移;`u32@12` = 条目数;每条 48 字节:`name[0x15]`、`ext[3]@0x15`、`u32 offset@0x18`(再 +0x10)、`u32 unpacked@0x1c`、`u32 packed@0x20`、`u8 comp@0x24`(0 = 直存,2 = Cocotte 压缩)。
- **VOICE/SREV*.PAK**(165 个包,编号 001–190 有洞,按通配枚举):全部直存,条目是 RIFF WAV,**MS-ADPCM 单声道**(约 22 KB/s ⇒ 4-bit);采样率**逐条读**,8,603 条里 44.1 kHz 8,096 条、48 kHz 507 条,不能假定全 44.1k。`tools/extract_voice.py` 逐条解出并记 `dataset/stats.csv`(pak, entry, sample_rate, bytes, seconds)。时长优先读 `fact` 块的样本数,没有就用 `data 长度 / block_align × samplesPerBlock`。
- **其他包**(后来为找歌曲才查清):`SONG/SRxx/SONG.ADP` = 整曲(见 §4.9);`KEY.PAK` = fortell 乐器采样(bdbd/guit/wind…,ADP1 单声道短样本);`SONG.PAK` = 背景图 + 曲名图;`BGM/TRACK*.BGM` = 标准 RIFF WAVE PCM 纯配乐;`EVCG.PAK` 236 条全部直存,其中 211 张 PNG:`srchr*` 立绘(320×480 / 340×480,RGBA)、`srfea*` 翅膀小图、`srey*` 眼部差分;朵朵(トルティニタ)的立绘是**红裙白衬衫扎发**那组:srchr010–019、122、139–143、149–151;戴帽子长双马尾、带音符的 srchr090–097、127–130、147 是芙铃(フォーニ),第一版 PV 我(Claude Code)认错了人,作者纠正;`EVBG.PAK` 140 张 PNG:`srbg*` 640×480 背景、`sran*` 640×1920/3840 竖排动画条;`EVSE.PAK` 60 条 RIFF WAV 音效;`SROP.MPG` 开场动画 640×480 60fps 189 s。全部用 `tools/extract_images.py` 按索引直接切出,不需要解码。
- 核对:每包条目数与文件尾对得上、随机抽几条 WAV 能播。

### 4.3 说话人映射与语料构建

语音文件名只有编号,不带角色。映射走脚本:

1. `SCRIPT.PAK` 186 条全是 Cocotte 压缩(comp=2)→ 用 `tools/ExtractScript.exe`(编译自 `ExtractScript.cs` + GARbro 的 `KogadoCocotte.cs`)解压 186/186 到 `dataset/kgo/`:`Scene.tbl` 1 个 + KGO 脚本 185 个。
2. `tools/build_voice_map.py` **直接读取** SymphonicRain-ENX 的反汇编 json(`tools/enx_jsons/`),按「Voice(id) → 紧邻 Text 的 [Name]」产出 `dataset/voice_map.csv`(scene, voice_id, speaker);第 1 步解出的本地 KGO 只用来做场景 001 的语音号交叉对齐,映射脚本不消费它。
3. `tools/prep_train_data.py` 按 speaker 分拣到 `dataset/train/torta/`(1,739 条,138.3 分钟)、`dataset/train/chris/`(771 条)。`dataset/DATASET-REPORT.md` 记数量与时长分布。

要点:**几乎全是日语对白**,没关系(§2);最长单条 20.7 s,没有任何 >25 s 的条目,说明 VOICE 包里**没有整首歌**。
说话人标签来自 **SymphonicRain-ENX 反汇编 json**(Switch/Steam 版脚本)里每句 Text 自带的 `[Name]` 前缀,`build_voice_map.py` 读的是这些 json,**不是**本地解出的 `dataset/kgo/`;本地 2010 版 KGO 只做了场景 001 的交叉对齐(语音号体系一致)。计数是映射行口径(Torta 1,741 行、Phorni 1,594、Fal 1,513、Chris 771),去重后的训练音频数是 1,739。标签不靠人耳或立绘判断——所以立绘认错人不影响训练集。

### 4.4 Applio 预处理与训练

- 预处理:`core.py preprocess`;特征提取:`core.py extract`,**CPU 核数设 2**(设 8 会卡死,见坑 4);F0 法 rmvpe,嵌入器 contentvec。
- 训练:朵朵跑到 **130 轮**;Chris 只跑了 5 轮就停(作者判「疑似毫无用武之地」,训练驱动脚本 `train-chris-driver.mjs` **禁止重拉**)。
- 导权重:`--save-every-weights` 没生效(`train.py` 收到的 argv[10] 是 False),所以从 `applio/logs/torta/G_*.pth` 用 `tools/export_weight.py` 导出 `torta_130e_manual.pth`;这一步需要一个 `applio/assets/config.json` 桩文件才跑得起来。
- 产物:`applio/logs/torta/torta_130e_manual.pth` + `torta.index`。已推到作者的**私有** GitHub 仓;语料、检查点、游戏素材**永不外传**。
- 系统卫生:训练前把睡眠超时关掉,训完必须复原(本机 AC 300 s / DC 180 s,用 `powercfg` 回读确认,第一次没生效重做了一遍)。
- 核对:loss 曲线只作参考;真正的验收是 §4.6 推理出来听。

### 4.5 干声分离(两级)

1. `audio-separator goodbye_src.wav --model_filename model_bs_roformer_ep_317_sdr_12.9755.ckpt` → `Vocals` / `Instrumental`。
2. 把第 1 级的 `Vocals` 再喂 `mel_band_roformer_karaoke_aufr33_viperx_sdr_10` → `(Vocals)` = **主唱**、`(Instrumental)` = **和声/伴唱**。两条都在 `stems-lead/`。
3. 试过但没用上:`UVR_MDXNET_KARA_2`、男/女和声专用模型——对本曲的问题段(见 §4.10)都分不干净。

核对:分离出的轨用 RMS(dBFS)看有没有内容——`−20 dBFS` 量级是真人声,`−45 dBFS` 以下基本是残留。

### 4.6 RVC 推理

主唱干声(4.5 的主唱轨)整曲喂 Applio。Applio 的 `core.py` 必须在 `applio/` 目录里跑,解释器用 `venv-applio`,路径给绝对或相对于 `applio/` 的(在 `clipboard/ai-cover/` 下执行):

```
( cd applio && ../venv-applio/Scripts/python.exe core.py infer \
    --input-path "$PWD/../stems-lead/<主唱干声>.flac" --output-path "$PWD/../lead.wav" \
    --pth-path "$PWD/logs/torta/torta_130e_manual.pth" --index-path "$PWD/logs/torta/torta.index" \
    --pitch 0 --index-rate 0.6 --protect 0.35 --f0-method rmvpe )
```

权威入口是 `bash tools/build_pitch_version.sh <标签> <半音>`,它内部就是这条命令。四份 shell 工具(`build_pitch_version.sh` / `fly_235.sh` / `window_variants.sh`)都按脚本自身位置推导根目录(`ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"`,给 Windows 程序的路径用 `cygpath -m` 转盘符形式),不再写死本机目录;`fly_235.sh` 开头检查两份输入存在,缺了直接报错退出(外审 150-02/07/08)。

整曲(3:38)在本机 GPU 上 12–42 s 一次。变体:`--pitch -2`(B 版)、`--formant-shifting --formant-qfrency 1.0 --formant-timbre 0.88`(A 版,只改音色不改音高)。

### 4.7 对齐与混音配方

混音分**两层**:下面这条是 **v23 基线混音**(只含 memory 窗自动化),`build_pitch_version.sh` 产的 B 版就是它;最终版在它之上还要跑 `tools/fly_235.sh`(2:34 飞入)、`tools/fly_107.sh`(1:07 飞入 + v4a 链)与 `tools/harmony_mix.py`(和声窗 −6 dB),顺序见 §7.2。基线配方:

```
ffmpeg -i <主唱> -i <伴奏> -filter_complex "
[0:a]atrim=start=6.594,asetpts=PTS-STARTPTS,volume=4dB,aresample=44100,
     volume=eval=frame:volume='if(between(t,65.5,67.7),0.841,if(between(t,65.35,65.5),1-0.159*(t-65.35)/0.15,if(between(t,67.7,67.85),0.841+0.159*(t-67.7)/0.15,1)))',apad[v];
[1:a]aresample=44100,volume=-2dB,
     volume=eval=frame:volume='if(between(t,65.5,67.7),1.259,if(between(t,65.35,65.5),1+0.259*(t-65.35)/0.15,if(between(t,67.7,67.85),1.259-0.259*(t-67.7)/0.15,1)))'[i];
[v][i]amix=inputs=2:duration=shortest:normalize=0,alimiter=limit=0.98[out]" -map "[out]" -c:a libmp3lame -b:a 320k out.mp3
```

- 主唱 +4 dB、伴奏 −2 dB 是耳裁定下来的平衡(最初伴奏喧宾夺主)。
- `amix normalize=0` 否则 ffmpeg 会把两路各砍一半;`alimiter 0.98` 防削波。
- `apad` 在主唱轨上:`amix duration=shortest` 会按最短输入截断,主唱轨短于伴奏就把歌尾砍掉(坑 8)。
- 65.5–67.7 s 是「memory」窗:主唱 ×0.841(−1.5 dB)、伴奏 ×1.259(+2 dB),两端 0.15 s 斜坡——**让官方伴奏里自带的和声顶上来**。这招在 2:34–2:41 又用了一次(§4.10)。
- 伴奏支路的 `aresample=44100` 是防御性补充(官方伴奏本来就是 44.1k),两份定稿脚本里没有这一项。
- 混响:v2b/v3b 用 pedalboard `Reverb(room_size=0.28, wet_level=0.16, dry_level=0.9)`,定稿不加。
- 核对:`ffprobe -v error -show_entries format=duration -of csv=p=0 out.mp3` = 218.86 s(3:38.86)。重编码后的 mp3 与输入 wav 的流哈希**不会**相同;只有「加标签(`-c copy`)前后」两个 mp3 才应相同,见 §7.2。

### 4.8 音高:高了多少、怎么降、降多少

朋友反馈「太高」。先量再动:

| 音源 | P10 | 中位 | P90 |
|---|---|---|---|
| 游戏对白(1,739 句语料) | — | D4 | — |
| 《秘密》游戏内实唱(SR03 分离人声;作者已确认是该曲) | A#3 | F4 | B4 |
| v23 / A 版(共振峰) | E4 | A#4 | D5 |
| B 版(−2) | D4 | G#4 | C5 |
| C 版(−4) | C4 | F#4 | A#4 |

工具:`tools/f0_range.py <wav>`(pyin,100–900 Hz,取有声帧的 P10 / 中位 / P90)。
读法:原曲把她推到比说话声区高约 8 半音、比她自己唱《秘密》高 5 半音的位置。
三版做法(`tools/build_pitch_version.sh <标签> <半音>` 一条命令):人声用 RVC `--pitch N` 重转(不是事后移调!),伴奏 `rubberband=pitch=2^(N/12)`,再走 4.7 配方。
结果:A 版音区没变(共振峰不动 F0);C 版音区最接近《秘密》但作者判「做作」;**B 版中选**。
高质量伴奏移调档(`pitchq=quality:transients=smooth:formant=preserved`)与默认档在 150–165 s 的谐波比只差 0.02,听不出本质区别(B3 版实测)。

### 4.9 游戏里的歌曲怎么挖出来(为了对照《秘密》)

- `SONG/SRxx/SONG.ADP` 头 16 字节:`ADP1` + `u32 每声道样本数@4` + `u32 采样率@8` + `u16 声道数@12`。**数据是 4-bit ADPCM**:每字节两个样本,低半字节 = 声道 1、高半字节 = 声道 2;不是标准 IMA,而是 GARbro `Hypatia/AudioADP.cs` 里那套 49 级量化表 + 16 项缩放表 + 步进表。
- 移植成 `tools/Adp1Decode.cs`,`csc -nologo -optimize Adp1Decode.cs` 编译(要 `cd tools` 后用裸文件名,见坑 15),18 首整曲解出到 `songs/`,2:36–3:53 不等,**都带演唱**(分离后人声轨 −20 ~ −25 dBFS)。
- 找《秘密》:`tools/song_fingerprint.py` 批量测 bpm/调式;谱面站给的是 E♭ 大调、70 bpm;命中 SR03 / SR13(D# 大调 = E♭,估拍 136 ≈ 2×68,估拍器二倍误报)。SR03 与 SR13 同长 156 s,疑似同曲两版。
- 之前的错误:把 ADP1 当 PCM 解了一遍,得到的是响亮噪声(−7 dBFS),谱平坦度 0.10;真音乐是 0.00003 量级、白噪声 0.56。**用这个数判「解对了没」**,不要靠「能出 bpm」——噪声也能估出 bpm。

### 4.10 两处病灶:主唱掉下去、和声接管

**现象**:1:01–1:07(as we weave / memory)和 2:34–2:41 两段,转换后要么颤抖碾碎、要么「苍白空灵」。

**定位**(逐秒量,不靠耳朵猜因果):

| 成品秒 | 第二副歌 主唱 / 和声 dB | 第一副歌对应位(−84.66 s)主唱 / 和声 dB |
|---|---|---|
| 154 | −30.3 / −17.6 | −19.1 / −23.7 |
| 155 | −36.8 / −15.5 | −17.1 / −24.8 |
| 157 | −22.8 / −20.3 | −19.0 / −27.5 |
| 159 | −20.2 / −21.1 | −17.6 / −25.2 |

第二段(2:34–2:41)由这张表坐实:**原唱主唱掉到 −30 dB 以下、和声顶上来**,分离出的「主唱轨」实际是和声混合物。第一段(1:01–1:07)当时的判据是 F0 逐帧标准差 160–180 音分与分离残留,没有做同样的能量表——「两段同根」是作者的判断加上第二段的证据,第一段未按同一尺子复核。多声部进 RVC ⇒ F0 乱飞 / 模型渲染发虚。作者先听出来,再由数字坐实。

**本次试过、都没解决的路**:分离模型换三种、F0 法换三种、index/protect 扫五组(读数差异 <2 dB、谐波比差 <0.05,耳裁无差)、局部压低/静音主唱、用和声轨做输入(多声部)、把 v23 人声 rubberband 移调(全曲空灵)。这只证明「本次这些组合没用」,不证明所有参数组合都无解。

**成功的路**:
1. **flying-in 移植**:同一首歌两个副歌是同词同旋律(两窗主唱色度相关 0.81),把健康那次的主唱切下来飞到病灶位置。第一次(v20):视频轴 68.66–71.60 ← 153.32–156.26(第二副歌飞到第一副歌);第二次(fly235):成品 154.0–160.6 ← 69.34–75.94(第一副歌飞到第二副歌),源轴各加 6.594。拼接两端 60–80 ms 交叉淡入淡出。
2. **官方和声复活**:该窗主唱 ×0.841、伴奏 ×1.259(4.7 的自动化),让官方伴奏里的和声接住。
3. 两者叠加(`goodbye_torta_fullB_FLYHARM235.mp3`)是**当时**的定稿(中间版 v2);之后 2:34 窗缩到只飞 Stitching、1:07 再飞一次、和声窗改为压低 −6 dB,最终版见 §0 与 §7.2。

核对:飞入后该窗主唱轨比原来高 2–4 dB(2:35 处 −18.1 对 −21.9);接缝处 `ffprobe` 总时长不变(218.86 s)。

### 4.11 PV

素材全部来自游戏本体。`tools/extract_images.py <游戏目录> [前缀]` 把 EVCG/EVBG 里的直存 PNG **全量**切到 `pv/assets/sprites/` 与 `pv/assets/bg/`(可用前缀参数限定,如 `srbg`);当前工作区里的精选是手工删出来的:立绘只留朵朵扎发的 16 张(srchr010–019、122、139–142、151),背景用 srbg024/026/054/084/165/184/284/296/305/354 十张——复建时按这两份清单删。封面不经提取器,是开场动画的一帧:
```
ffmpeg -y -ss 43 -i "<游戏目录>/SROP.MPG" -frames:v 1 -vf "crop=640:360:0:60,scale=1920:1080:flags=lanczos" pv/cover.jpg
```
(45 s 处同镜头烙着制作人员字幕,43 s 无字)。
现行脚本 `tools/build_pv3.py`(`build_pv2.py` 加歌词层):PIL 合成每场景「背景 + 闭嘴立绘」「背景 + 张嘴立绘」两张 1080p 图,逐帧(30 fps)按主唱轨包络选张嘴或闭嘴(RMS > −32 dBFS 张嘴,持续张嘴每 0.32 s 插两帧闭嘴),场景间 1 s 交叉淡,歌词每行一张 RGBA 图在内存里按时间轴 alpha 混合到底部,整段 rawvideo 管道喂 ffmpeg 出 yuv420p H.264(**必须 yuv420p**,yuv444p 多数播放器打不开)。
`tools/build_pv.py` 是第一版(OP 实拍 + ffmpeg xfade),**已废**:它引用的芙铃立绘与翅膀已删、OP 路径写死,不要再跑。
歌词时间轴:网易云歌词接口对**歌曲 id** 可匿名取(`api/song/lyric?id=2629122902&lv=1`,id 由 `api/search/get` 查得;专辑接口才要绑手机),`pv/lyrics_official.lrc` 就是官方 LRC;用人声包络在 0:34 / 0:48 / 1:02 / 1:31 四处段落起唱核过,官方轴与成品轴差 ≤0.25 s,只有首行(官方 2.56 s)按实测起唱改到 1.26 s。faster-whisper large-v3 只作历史备选:它的词起点普遍比真实起唱早 1–2 s,且 **vad_filter 必须关**(开着只剩 62 词)。
**2026-09-05 现行版 `tools/build_pv9.py`**(v3 那套立绘嘴型已整体撤掉:游戏立绘 012/151 是小口/大口不是闭/张,作者裁定 PV 不放人)。切镜按作者给的「歌词行区间→背景」表(脚本里的 `PLAN`),不缩放,镜头间 0.8 s 叠化。雨效三层:
- **雨丝层**:程序合成的 8 帧斜向雨丝(`pv/assets/rain/mine/streak8_1..8.png`,抖动网格保证密度均匀,8 fps 循环)。从游戏动画条差分抽出来的「雨层」大头其实是地面涟漪,别走那条路。
- **室内只在玻璃上下雨**:游戏背景 PNG 的 **alpha 通道就是玻璃掩膜**(游戏本体把天空/雨层垫在窗后,alpha 255=玻璃,0=柱子/窗棂/天花板/椅子)。这比手标矩形、颜色判据、外部模型手标多边形都准,一行 `src.split()[3]` 就拿到;只有 `srbg*` 静态图有,`sran*` 动画条没有。
- **动画条**:街道/车站条叠 45% 雨丝;拱廊(sran184a,自带喷泉动画)与火车两条(sran370a/352a,剧情是先过隧道再进晴天)**不叠雨**——作者裁定,雨要合剧情逻辑不是越多越好。370a 八帧 = 隧道内 6 帧 + 出隧道 2 帧,整条 8 fps 循环会每秒闪一下;做法是只循环前 6 帧,出隧道两帧放在镜头末尾叠化处接 352a 的晴夜。(手标玻璃多边形 `train_mask()` 留在脚本里备用。)
速度:每帧在 1080p 浮点数组上重算合成是瓶颈(python 约 700 s vs ffmpeg 190 s)。静态镜头 × 8 个雨相位是有限组合,预合成成 uint8 缓存后每帧只剩一次拷贝加歌词混合。歌词层就地写缓存帧会叠影,必须先 copy。编码 libx264 veryfast、**必须 yuv420p**(yuv444p 播放器打不开);h264_nvenc 在本机用不了(驱动 591.91 低于这版 ffmpeg 要求的 610)。
投稿文案与平台步骤另有稿件包,不入仓。

---

## 5. 踩坑清单(现象 → 根因 → 怎么发现 → 怎么绕)

1. **管道吞退出码**:`cmd | tail` 永远显示成功 → shell 只看管道最后一个命令的退出码 → 「成功」但产物不存在 → 不接管道,跑完 `ls` 产物。
2. **audio-separator 报 audioread 缺失 / basic-pitch 其实没装上**:装依赖时的错被 `| tail -2` 吞了 → 同上;每次装完 `pip show` 核。
3. **m4a + 中文文件名「Format not recognised」**:分离器走 soundfile,不认 m4a,也对非 ASCII 路径不稳 → 先 ffmpeg 转 WAV、改 ASCII 名。
4. **预处理跑了两遍互相踩、extract 卡死**:后台任务被重复拉起;`--cpu-cores 8` 在本机卡住 → 杀进程、隔离旧 `logs/torta`、核数改 2。
5. **误判「两个训练在跑」**:venv 的 `python.exe` 是壳,真解释器是另一个进程,Git Bash 的 `ps` 只看得到一半 → 用 CIM(`Get-CimInstance Win32_Process`)看完整命令行。
6. **`--save-every-weights` 不落权重**:参数没传进 `train.py`(argv[10]=False)→ 从 `G_` 检查点自己导(`export_weight.py`),需要补 `assets/config.json`。
7. **torch cu128 频道消失、强制重装被 DLL 锁挡住**:装包渠道变了;运行中的进程占着 DLL → 换 cu130;另开一个 venv 而不是覆盖。
8. **`amix duration=shortest` 把歌尾砍了**:一条短轨决定总长 → 短轨 `apad`,或先把短层预混进长轨。
9. **和声层放早了 6.594 s / 拼接处 50 ms 重复 / 补丁窗太短切掉 memory 尾音**:视频轴与官方轴混用;切点算重叠 → 所有切点写成「源轴」并在脚本头注明;拼前 `ffprobe` 总时长核对。
10. **多声部 F0 抖动 160–180 音分**:两条基频叠着 → 本次五组参数扫描都没解决,最终换输入(flying-in)才过。
11. **「无词哼鸣」叙事被作者戳穿**:我(Claude Code)把听不清的段描述成「哼鸣」,实际是碾碎的词 → **不要编听感**;报能量、F0、时长这些数,听感留给作者。
12. **SONG.ADP 当 PCM 解成噪声,还据此说「游戏里只有伴奏」**:格式猜错;bpm 估计器对噪声也给数 → 谱平坦度判据(0.10 vs 0.00003);找规格文件(GARbro)再动手。
13. **BGM/TRACK14 被当成《秘密》**:69.8 bpm 正好等于谱面站的 70,但它是纯配乐(人声轨 −85 dBFS)→ bpm 相同不等于同曲;人声轨 dBFS 才是「有没有唱」的判据。
14. **rubberband 移人声全曲空灵**(B2 版)→ 机制未核(通常归于相位声码器类算法的相位/瞬态处理)→ 工艺结论:人声只走 RVC `--pitch`,伴奏才用 rubberband。
15. **csc 把 `/nologo` 当路径**:Git Bash 把 `/xxx` 转成 Windows 路径 → 用 `-nologo`,且 `cd tools` 后用裸文件名。
16. **PowerShell 杀进程把自己杀了**:按命令行关键字匹配,匹配到了正在跑这条命令的 powershell 本身 → 先列再杀,或排除 `$PID`。
17. **GPU 被后台队列吃满**:为找《秘密》拉了 18 首整曲的分离队列(每首 3–5 分钟)→ 作者问「GPU 怎么 100%」才想起 → 后台重活开工前说一声,不需要的队列及时杀。
18. **后台任务被会话管理器杀掉**:用 `( nohup ... & )` 起孤儿进程才活得过任务清理;判「在不在跑」看进程与产物,不看日志尾行。
19. **`cd` 在 Bash 工具里会残留**:下一条命令的相对路径全错(脚本写到了别的目录)→ 脚本内第一行 `cd` 到工作目录;工程根的命令用绝对工作目录起手。

---

## 6. 我(Claude Code)想加的

**验证纪律:每一步用什么数字核,不靠耳朵断因果。**
- 「有没有内容」:轨的 RMS dBFS(本项目这批音轨、这套分离模型下的经验判据:−20 真声、−45 以下残留、−85 空;换模型或归一化方式要重标)。
- 「解码对没对」:谱平坦度(音乐 1e-5 ~ 1e-3;噪声 0.5 上下)。
- 「两段是不是同词同旋律」:色度逐帧余弦(本次 0.81 判可飞;阈值 0.7 是自定的,未做过更多样本校准)。
- 「哪一层坏了」:主唱轨 / 伴奏轨 / 混音分别与好版本逐秒比 RMS、谱质心、4–8k/1–2k 能量比、谐波比(HPSS)、F0 中位。差异 <2 dB、<0.05 时**说「读数分不出」**,不要硬归因;然后设计能区分原因的对照版(B2/B3 那次就是这么把伴奏移调器排除掉的)。
- 「耳裁」是唯一终审:所有数字只负责缩小范围与排除;最后一步永远是作者听。

**版本命名与台账。** v1–v23 每版一句改动、一句耳裁结果;A/B/C 音高版、B2/B3 对照版、P1–P5 参数扫描、FLY/HARM/FLYHARM 修法版,名字里带做法而不是日期。同一个窗口的切点常数(6.594、84.66、65.5–67.7、154.0–160.6)写进脚本里(`fly_235.sh` 在头注,`build_pitch_version.sh` 只埋在命令体——外审指出这点不一致,以后统一放头注/变量区),不散在聊天里。

**什么时候该停下问。** 只有三类:不可逆(发布、删除)、要作者亲签的取舍(音区选哪版、这段要不要牺牲和声)、只有作者能做的事(耳裁、登录)。「工作量大」不是理由——重建一个版本往往就是一条脚本一分钟。

---

## 7. 附录

### 7.1 文件清单(相对 `clipboard/ai-cover/`)

| 路径 | 内容 |
|---|---|
| `goodbye_torta_final_20260904b.mp3` | **最终版**(投稿件;音频 MD5 `c8cc19283ea1bd08fce25299aa8601b2`,−12.2 LUFS) |
| `goodbye_torta_final_20260904.mp3` | 最终版的前一步(= v3b;窗口外与最终版一致) |
| `goodbye_torta_final_v2.mp3` / `_v3.mp3` / `_v3b.mp3` | 中间版(v2 = FLYHARM235 加标签;v3/v3b 见 §0) |
| `goodbye_torta_final.mp3` | 旧版 v23(原调) |
| `goodbye_torta_fullA_formant.mp3` / `fullB_down2.mp3` / `fullC_down4.mp3` | 音高三版 |
| `goodbye_torta_fullB2_v23lead_shift.mp3` / `fullB3_rvclead_instrb2.mp3` | 归因对照版 |
| `goodbye_torta_fullB_FLY235.mp3` / `HARM235.mp3` / `FLYHARM235.mp3` | 2:34–2:41 三种修法 |
| `clips/` | 各版 2:30–2:45 片段 |
| `torta_lead_full.wav`、`torta_lead_v20.wav`、`leadA_*`、`leadB_*`、`leadB_fly235.wav`、`leadB_fly235_107.wav` | 各版人声轨(最后一个是最终版用的) |
| `inst_full_down2.wav`、`inst_full_down2_rb2.wav` | 伴奏 −2(默认档 / 高质量档) |
| `stems-inst/` | 官方伴奏(−2)经 karaoke 模型拆成的和声轨 / 纯伴奏(最终版压和声用) |
| `official/goodbye_instrumental_official.mp3` | 官方伴奏 |
| `stems-lead/` | 两级分离产物(主唱 / 和声) |
| `songs/`、`songs-stems/` | 游戏 18 首整曲(正确解码)与分离产物;`songs-wrong-pcm-decode/` 是错误解码留档 |
| `dataset/` | 语料(`raw/`、`train/torta/`、`train/chris/`、`voice_map.csv`、`stats.csv`、`DATASET-REPORT.md`、`kgo/`) |
| `applio/logs/torta/` | `torta_130e_manual.pth`、`torta.index`、`G_*` 检查点 |
| `applio/logs/chris/` | Chris 5 轮粗胚(停) |
| `tools/` | 本文所有脚本与移植源码 |
| `venv/`、`venv-train/`、`venv-applio/` | 三个虚拟环境 |

### 7.2 最终版复跑命令(从 B 版人声与伴奏出发)

目标产物是 `goodbye_torta_final_20260904b.mp3`。两种入口不要混:**从主唱干声复建**(1→2→3→4→5)或**从现成中间件复跑**(直接 2→5,前提是目录里已有 `leadB_spliced.wav` 与 `inst_full_down2.wav`)。都在 `clipboard/ai-cover/` 下跑。

```
# 1. B 版整曲(RVC --pitch -2、伴奏 rubberband、v20 移植、v23 基线配方);产物 leadB_spliced.wav / inst_full_B.wav
bash tools/build_pitch_version.sh B -2
cp inst_full_B.wav inst_full_down2.wav      # 后面的脚本固定读 inst_full_down2.wav(历史命名)
# 2. 2:34 窗只飞 Stitching(154.0–157.2 ← 69.32–72.52);产物 leadB_fly235.wav(顺带出三个中间版 mp3,不用管)
bash tools/fly_235.sh
# 3. 1:07 memory 再飞一次(65.45–69.2 ← 150.13–153.88)+ v4a 混音链;产物 leadB_fly235_107.wav 与
#    goodbye_torta_final_v4a_FLY107_NOHARM.mp3(= goodbye_torta_final_20260904.mp3,最终版的前一步)
bash tools/fly_107.sh
# 4. 把 −2 半音的官方伴奏拆成 和声轨 / 纯伴奏(audio-separator,karaoke 模型;venv-train)
audio-separator inst_full_down2.wav --model_filename mel_band_roformer_karaoke_aufr33_viperx_sdr_10.1956.ckpt --output_dir stems-inst --output_format WAV
# 5. 最终版:只在 146.5–160.5 s(成品轴)把和声轨压 −6 dB,重走 v4a 链(主唱 +4 dB),对齐 −12 LUFS
LEAD_DB=4 venv/Scripts/python.exe tools/harmony_mix.py -6 20260904b 146.5-160.5
# 核对:窗口外与第 3 步产物 5 秒 RMS 差 0.0 dB、窗口内低 0.3–0.5 dB;时长 218.86 s
ffprobe -v error -show_entries format=duration -of csv=p=0 goodbye_torta_final_20260904b.mp3
```

**复跑不保证逐位一致。** 2026-09-05 用上面第 5 步原样重跑,得到的文件比投稿件整体响 0.7 dB(窗口内外一致地偏移),和声窗的相对压低量一样;整体电平来自 `harmony_mix.py` 末尾按 ebur128 实测做的 −12 LUFS 对齐,两次实测差了零点几 dB 的原因没有查清,如实记在这里。要确认手上的是投稿件,认 §7.1 里的 MD5,不认复跑。

### 7.3 关键常数

| 常数 | 值 | 来源 |
|---|---|---|
| 视频轴 − 官方轴 | 6.594 s | 互相关 |
| 第二副歌 − 第一副歌 | 84.66 s | 互相关 + v20 移植验证 |
| memory 窗 | 65.5–67.7 s(斜坡 0.15 s) | 耳裁 |
| 2:34 窗(最终版) | 154.0–157.2 s(飞入源 69.32–72.52,只飞 Stitching) | 逐秒 RMS + 逐句比词;首版 154.0–160.6 盖错了词 |
| 1:07 窗(最终版) | 65.45–69.2 s(飞入源 150.13–153.88) | 包络互相关 + 起音低谷 |
| 和声压低窗(最终版) | 146.5–160.5 s,和声轨 −6 dB(0.3 s 平滑) | 耳裁 |
| 降 2 半音 | rubberband pitch = 0.890899 | 2^(−2/12) |
| 混音 | 主唱 +4 dB、伴奏 −2 dB、normalize=0、limiter 0.98 | 耳裁 |
| 推理 | index 0.6、protect 0.35、rmvpe | 默认 + 扫描无差 |
