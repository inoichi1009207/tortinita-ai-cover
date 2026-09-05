#!/usr/bin/env bash
# 2:35–2:40 窗口 RVC 参数扫描:源人声切 150–172s(源时间轴)→ 各参数重转(−2)→ 拼回 leadB_spliced(源 156.6–171.6s 换入,0.1s 交叉淡)→ B 伴奏混音 → 切 2:30–2:45 片段
set -e; ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; ROOTW="$(cygpath -m "$ROOT")"; cd "$ROOT"; mkdir -p clips
LEAD="stems-lead/goodbye_src_(Vocals)_model_bs_roformer_ep_317_sdr_12_(Vocals)_mel_band_roformer_karaoke_aufr33_viperx_sdr_10.flac"
ffmpeg -y -loglevel error -ss 150 -t 22 -i "$LEAD" -c:a flac win_src.flac
run(){ N=$1; shift
  ( cd applio && ../venv-applio/Scripts/python.exe core.py infer --input-path "$ROOTW/win_src.flac" --output-path "$ROOTW/win_$N.wav" --pth-path "$ROOTW/applio/logs/torta/torta_130e_manual.pth" --index-path "$ROOTW/applio/logs/torta/torta.index" --pitch -2 "$@" ) >> win_variants.log 2>&1
  ffmpeg -y -loglevel error -i leadB_spliced.wav -i win_$N.wav -filter_complex "[0:a]asplit=2[h][t];[h]atrim=0:156.7,afade=t=out:st=156.6:d=0.1[head];[t]atrim=171.5,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.1[tail];[1:a]atrim=6.6:21.6,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.1,afade=t=out:st=14.9:d=0.1[mid];[head][mid][tail]concat=n=3:v=0:a=1[out]" -map "[out]" leadB_$N.wav
  ffmpeg -y -loglevel error -i leadB_$N.wav -i inst_full_down2.wav -filter_complex "[0:a]atrim=start=6.594,asetpts=PTS-STARTPTS,volume=4dB,aresample=44100,apad[v];[1:a]volume=-2dB[i];[v][i]amix=inputs=2:duration=shortest:normalize=0,alimiter=limit=0.98[out]" -map "[out]" -ss 150 -t 15 -c:a libmp3lame -b:a 192k clips/B_win_${N}_230-245.mp3
  echo "OK $N $(ffprobe -v error -show_entries format=duration -of csv=p=0 clips/B_win_${N}_230-245.mp3)"
}
run P1_protect050 --index-rate 0.6 --protect 0.5 --f0-method rmvpe
run P2_index030   --index-rate 0.3 --protect 0.35 --f0-method rmvpe
run P3_crepe      --index-rate 0.6 --protect 0.35 --f0-method crepe
run P4_index085   --index-rate 0.85 --protect 0.35 --f0-method rmvpe
run P5_fcpe       --index-rate 0.6 --protect 0.35 --f0-method fcpe
