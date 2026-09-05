"""faster-whisper large-v3 逐词时间戳 → pv/whisper_words.json(源轴 src 与成品轴 t=src−6.594)。
GPU 需要 CUDA 12 的 cuBLAS/cuDNN DLL(pip 的 nvidia-cublas-cu12 / nvidia-cudnn-cu12),脚本自动把它们的 bin 加进 PATH;加载失败回退 CPU int8。
用法(在 clipboard/ai-cover/ 下):HF_HOME=D:/hf-home venv-train/Scripts/python.exe tools/whisper_words.py"""
import os, sys, glob, json, time
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
site = os.path.join('venv-train', 'Lib', 'site-packages', 'nvidia')
for sub in ('cublas', 'cudnn', 'cuda_runtime'):
    b = os.path.abspath(os.path.join(site, sub, 'bin'))
    if os.path.isdir(b):
        os.environ['PATH'] = b + os.pathsep + os.environ['PATH']
        if hasattr(os, 'add_dll_directory'): os.add_dll_directory(b)
import ctranslate2, faster_whisper
from faster_whisper import WhisperModel
src = glob.glob('stems-lead/*_(Vocals)_mel_band_roformer_karaoke*')[0]
def run(dev, ct):
    model = WhisperModel('large-v3', device=dev, compute_type=ct, download_root='D:/hf-home')
    segs, info = model.transcribe(src, language='en', word_timestamps=True, beam_size=5, vad_filter=True,
                                  initial_prompt="Song lyrics, English pop ballad.")
    return list(segs), info
t0 = time.time()
try:
    segs, info = run('cuda', 'float16'); dev = 'cuda'
except Exception as e:
    print('GPU 路径失败,回退 CPU:', str(e)[:120]); segs, info = run('cpu', 'int8'); dev = 'cpu'
lines, words = [], []
for s in segs:
    lines.append({'start': round(s.start, 3), 'end': round(s.end, 3), 'text': s.text.strip(), 'avg_logprob': round(s.avg_logprob, 3)})
    for w in (s.words or []):
        words.append({'src': round(w.start, 3), 'src_end': round(w.end, 3), 't': round(w.start - 6.594, 3), 't_end': round(w.end - 6.594, 3), 'w': w.word.strip(), 'p': round(w.probability, 3)})
json.dump({'device': dev, 'model': 'large-v3', 'language': info.language, 'lang_prob': round(info.language_probability, 3), 'duration': info.duration,
           'lines': lines, 'words': words}, open('pv/whisper_words.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('device', dev, 'lang', info.language, round(info.language_probability, 3), 'dur', round(info.duration, 1), 'lines', len(lines), 'words', len(words), '耗时 %.0fs' % (time.time() - t0))
for l in lines[:8]: print(f"{l['start']:7.2f}-{l['end']:7.2f} {l['text']}")
