#!/usr/bin/env bash
# 1:07 memory 再飞(r2):成品 65.45–69.2 ← 150.13–153.88(偏移 84.68,包络互相关);r1 的 65.7 切在 Me 起音(65.6)之后,出了 "Mememory"。源轴 +6.594。
# 在 leadB_fly235.wav 基础上再飞一次 → leadB_fly235_107.wav;然后按 v4a 混音链出两版:KEEP(保留 memory 窗自动化)/ NOHARM(去掉 memory 窗自动化)
set -e; ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"; mkdir -p clips
[ -f leadB_fly235.wav ] || { echo "缺 leadB_fly235.wav(先跑 fly_235.sh)"; exit 2; }
PY="$ROOT/venv/Scripts/python.exe"; "$PY" -c "import sys" || { echo "解释器不可用: $PY"; exit 2; }
T0=65.45; T1=69.2; DD0=150.13; DD1=153.88; OFF=6.594   # 成品轴单源:65.45–69.2 ← 150.13–153.88(偏移 84.68,包络互相关;刀口在能量低谷)
"$PY" tools/lyric_window_check.py $T0 $T1 $DD0 $DD1 || exit 2
S0=$(awk "BEGIN{printf \"%.3f\", $T0+$OFF}"); S1=$(awk "BEGIN{printf \"%.3f\", $T1+$OFF}"); D0=$(awk "BEGIN{printf \"%.3f\", $DD0+$OFF}"); D1=$(awk "BEGIN{printf \"%.3f\", $DD1+$OFF}")
HEADFADE=$(awk "BEGIN{printf \"%.3f\", $S0-0.06}"); PATCHFADE=$(awk "BEGIN{printf \"%.3f\", $T1-$T0-0.06}")
ffmpeg -y -loglevel error -i leadB_fly235.wav -filter_complex "[0:a]asplit=3[a1][a2][a3];[a1]atrim=0:$S0,afade=t=out:st=$HEADFADE:d=0.06[head];[a3]atrim=$S1,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.06[tail];[a2]atrim=$D0:$D1,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.06,afade=t=out:st=$PATCHFADE:d=0.06[patch];[head][patch][tail]concat=n=3:v=0:a=1[out]" -map "[out]" leadB_fly235_107.wav
VOL_V="volume=eval=frame:volume='if(between(t,157.3,162.0),0.841,if(between(t,157.15,157.3),1-0.159*(t-157.15)/0.15,if(between(t,162.0,162.15),0.841+0.159*(t-162.0)/0.15,1)))'"
VOL_I="volume=eval=frame:volume='if(between(t,157.3,162.0),1.259,if(between(t,157.15,157.3),1+0.259*(t-157.15)/0.15,if(between(t,162.0,162.15),1.259-0.259*(t-162.0)/0.15,1)))'"
MEM_V="volume=eval=frame:volume='if(between(t,65.5,67.7),0.841,if(between(t,65.35,65.5),1-0.159*(t-65.35)/0.15,if(between(t,67.7,67.85),0.841+0.159*(t-67.7)/0.15,1)))'"
MEM_I="volume=eval=frame:volume='if(between(t,65.5,67.7),1.259,if(between(t,65.35,65.5),1+0.259*(t-65.35)/0.15,if(between(t,67.7,67.85),1.259-0.259*(t-67.7)/0.15,1)))'"
mixv4a(){ # 名 主唱滤镜串 伴奏滤镜串  (v4a 链:伴奏 −2dB + 250Hz −2dB + 温和侧链 2:1;后段响度补偿 +1.2dB)
  ffmpeg -y -loglevel error -i leadB_fly235_107.wav -i inst_full_down2.wav -filter_complex "[0:a]atrim=start=6.594,asetpts=PTS-STARTPTS,volume=4dB,aresample=44100$2,apad,asplit=2[v][sc];[1:a]volume=-2dB$3,equalizer=f=250:t=q:w=1.2:g=-2[i0];[i0][sc]sidechaincompress=threshold=0.1:ratio=2:attack=20:release=250:makeup=1:level_sc=1[i];[v][i]amix=inputs=2:duration=shortest:normalize=0,volume=1.2dB,alimiter=limit=0.98[out]" -map "[out]" -c:a libmp3lame -b:a 320k goodbye_torta_final_v4a_$1.mp3
  ffmpeg -y -loglevel error -ss 60 -t 15 -i goodbye_torta_final_v4a_$1.mp3 -c:a libmp3lame -b:a 192k clips/v4a_$1_100-115.mp3
  echo "OK $1 $(ffprobe -v error -show_entries format=duration -of csv=p=0 goodbye_torta_final_v4a_$1.mp3)"
}
mixv4a FLY107_KEEP ",$MEM_V,$VOL_V" ",$MEM_I,$VOL_I"
mixv4a FLY107_NOHARM ",$VOL_V" ",$VOL_I"
