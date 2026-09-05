"""从 G_ 检查点手动提取推理权重(绕开 core.py 旗标失传问题)。训练进程零接触。"""
import os, sys, json, torch
from types import SimpleNamespace

os.chdir(r"D:\test\clipboard\ai-cover\applio")
sys.path.insert(0, os.getcwd())
from rvc.train.process.extract_model import extract_model

def ns(d):
    if isinstance(d, dict):
        return SimpleNamespace(**{k: ns(v) for k, v in d.items()})
    return d

hps = ns(json.load(open("logs/torta/config.json", encoding="utf-8")))
ck = torch.load("logs/torta/G_2333333.pth", map_location="cpu", weights_only=True)
print("ckpt keys:", list(ck.keys()))
state = ck["model"]
epoch = int(ck.get("iteration", 0))
out = f"logs/torta/torta_{epoch}e_manual.pth"
extract_model(ckpt=state, sr=hps.data.sample_rate, name="torta", model_path=out,
              epoch=epoch, step=0, hps=hps, vocoder="HiFi-GAN")
print("OK", out, os.path.getsize(out) if os.path.exists(out) else "MISSING")
