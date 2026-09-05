#!/usr/bin/env bash
# 用法: build_pitch_version.sh <标签> <半音数(负=降)>   例: build_pitch_version.sh C -4
# 与 A/B 版同一条工艺:RVC 整曲重转(仅改 --pitch)→ v20 移植拼接 → 官方伴奏 rubberband 同步移调 → v23 混音自动化
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; ROOTW="$(cygpath -m "$ROOT")"; cd "$ROOT"   # 根目录按脚本位置推导;ROOTW=盘符路径给 Windows 程序
[ -n "$2" ] || { echo "用法: $0 <标签> <半音数>"; exit 2; }
X=$1; ST=$2; R=$("$ROOT/venv/Scripts/python.exe" -c "print(2**($ST/12))")
LEAD="stems-lead/goodbye_src_(Vocals)_model_bs_roformer_ep_317_sdr_12_(Vocals)_mel_band_roformer_karaoke_aufr33_viperx_sdr_10.flac"
( cd applio && ../venv-applio/Scripts/python.exe core.py infer --input-path "$ROOTW/$LEAD" --output-path "$ROOTW/lead${X}_full.wav" --pth-path "$ROOTW/applio/logs/torta/torta_130e_manual.pth" --index-path "$ROOTW/applio/logs/torta/torta.index" --pitch $ST --index-rate 0.6 --protect 0.35 --f0-method rmvpe )
ffmpeg -y -loglevel error -i official/goodbye_instrumental_official.mp3 -ar 44100 -af "rubberband=pitch=$R" inst_full_${X}.wav
ffmpeg -y -loglevel error -i lead${X}_full.wav -filter_complex "[0:a]asplit=3[a1][a2][a3];[a1]atrim=0:68.66,afade=t=out:st=68.60:d=0.06[head];[a3]atrim=71.60,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.06[tail];[a2]atrim=153.32:156.26,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.06,afade=t=out:st=2.88:d=0.06[patch];[head][patch][tail]concat=n=3:v=0:a=1[out]" -map "[out]" lead${X}_spliced.wav
ffmpeg -y -loglevel error -i lead${X}_spliced.wav -i inst_full_${X}.wav -filter_complex "[0:a]atrim=start=6.594,asetpts=PTS-STARTPTS,volume=4dB,aresample=44100,volume=eval=frame:volume='if(between(t,65.5,67.7),0.841,if(between(t,65.35,65.5),1-0.159*(t-65.35)/0.15,if(between(t,67.7,67.85),0.841+0.159*(t-67.7)/0.15,1)))',apad[v];[1:a]volume=-2dB,volume=eval=frame:volume='if(between(t,65.5,67.7),1.259,if(between(t,65.35,65.5),1+0.259*(t-65.35)/0.15,if(between(t,67.7,67.85),1.259-0.259*(t-67.7)/0.15,1)))'[i];[v][i]amix=inputs=2:duration=shortest:normalize=0,alimiter=limit=0.98[out]" -map "[out]" -c:a libmp3lame -b:a 320k goodbye_torta_full${X}_down$(( -ST )).mp3
ffprobe -v error -show_entries format=duration -of csv=p=0 goodbye_torta_full${X}_down$(( -ST )).mp3
