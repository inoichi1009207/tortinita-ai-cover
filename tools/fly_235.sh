#!/usr/bin/env bash
# 2:35–2:40 修法三版:FLY=第一副歌对应窗主唱飞入(成品 154.0–160.6 ← 69.34–75.94,源轴+6.594);HARM=官方和声复活(该窗主唱 −1.5dB/伴奏 +2dB);FLYHARM=两者叠加
set -e; ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; ROOTW="$(cygpath -m "$ROOT")"; cd "$ROOT"; mkdir -p clips
for f in leadB_spliced.wav inst_full_down2.wav; do [ -f "$f" ] || { echo "缺输入 $f(先跑 build_pitch_version.sh B -2 并 cp inst_full_B.wav inst_full_down2.wav)"; exit 2; }; done
PY="$ROOT/venv/Scripts/python.exe"; "$PY" -c "import sys" || { echo "解释器不可用: $PY"; exit 2; }
T0=154.0; T1=157.2; DD0=69.32; DD1=72.52; OFF=6.594   # 成品轴单源:只飞 Stitching(偏移 84.68);r1 飞到 160.6 把第一副歌 "I am yours" 盖到 "You and I'll be alright" 上,用户听出唱错词
"$PY" tools/lyric_window_check.py $T0 $T1 $DD0 $DD1 || exit 2
S0=$(awk "BEGIN{printf \"%.3f\", $T0+$OFF}"); S1=$(awk "BEGIN{printf \"%.3f\", $T1+$OFF}"); D0=$(awk "BEGIN{printf \"%.3f\", $DD0+$OFF}"); D1=$(awk "BEGIN{printf \"%.3f\", $DD1+$OFF}")
HEADFADE=$(awk "BEGIN{printf \"%.3f\", $S0-0.06}"); PATCHFADE=$(awk "BEGIN{printf \"%.3f\", $T1-$T0-0.06}")
ffmpeg -y -loglevel error -i leadB_spliced.wav -filter_complex "[0:a]asplit=3[a1][a2][a3];[a1]atrim=0:$S0,afade=t=out:st=$HEADFADE:d=0.06[head];[a3]atrim=$S1,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.06[tail];[a2]atrim=$D0:$D1,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.06,afade=t=out:st=$PATCHFADE:d=0.06[patch];[head][patch][tail]concat=n=3:v=0:a=1[out]" -map "[out]" leadB_fly235.wav
ffprobe -v error -show_entries format=duration -of csv=p=0 leadB_fly235.wav
VOL_V="volume=eval=frame:volume='if(between(t,157.3,162.0),0.841,if(between(t,157.15,157.3),1-0.159*(t-157.15)/0.15,if(between(t,162.0,162.15),0.841+0.159*(t-162.0)/0.15,1)))'"
VOL_I="volume=eval=frame:volume='if(between(t,157.3,162.0),1.259,if(between(t,157.15,157.3),1+0.259*(t-157.15)/0.15,if(between(t,162.0,162.15),1.259-0.259*(t-162.0)/0.15,1)))'"
MEM_V="volume=eval=frame:volume='if(between(t,65.5,67.7),0.841,if(between(t,65.35,65.5),1-0.159*(t-65.35)/0.15,if(between(t,67.7,67.85),0.841+0.159*(t-67.7)/0.15,1)))'"
MEM_I="volume=eval=frame:volume='if(between(t,65.5,67.7),1.259,if(between(t,65.35,65.5),1+0.259*(t-65.35)/0.15,if(between(t,67.7,67.85),1.259-0.259*(t-67.7)/0.15,1)))'"
mix(){ # 名 主唱 额外主唱滤镜 额外伴奏滤镜
  ffmpeg -y -loglevel error -i "$2" -i inst_full_down2.wav -filter_complex "[0:a]atrim=start=6.594,asetpts=PTS-STARTPTS,volume=4dB,aresample=44100,$MEM_V$3,apad[v];[1:a]volume=-2dB,$MEM_I$4[i];[v][i]amix=inputs=2:duration=shortest:normalize=0,alimiter=limit=0.98[out]" -map "[out]" -c:a libmp3lame -b:a 320k goodbye_torta_fullB_$1.mp3
  ffmpeg -y -loglevel error -ss 150 -t 15 -i goodbye_torta_fullB_$1.mp3 -c:a libmp3lame -b:a 192k clips/B_$1_230-245.mp3
  echo "OK $1 $(ffprobe -v error -show_entries format=duration -of csv=p=0 goodbye_torta_fullB_$1.mp3)"
}
mix FLY235 leadB_fly235.wav "" ""
mix HARM235 leadB_spliced.wav ",$VOL_V" ",$VOL_I"
mix FLYHARM235 leadB_fly235.wav ",$VOL_V" ",$VOL_I"
