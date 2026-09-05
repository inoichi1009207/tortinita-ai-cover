// 批138 条件4 排队件:Chris(库里斯)训练驱动——与 Torta 串行,GPU 只有一块,
// 【必须等 train-torta-driver.mjs 的 train 步结束/被叫停后才发车】
// 跑法: node train-chris-driver.mjs
// 与 Torta 驱动唯一差异:model-name=chris、数据集路径、无 prerequisites(底模已就位)
import { spawnSync } from 'node:child_process';
import { appendFileSync } from 'node:fs';

const PY = 'D:/test/clipboard/ai-cover/venv-applio/Scripts/python.exe';
const APPLIO = 'D:/test/clipboard/ai-cover/applio';
const LOG = 'D:/test/clipboard/ai-cover/train-chris.log';
const DATASET = 'D:/test/clipboard/ai-cover/dataset/train/chris';

const log = (s) => { const line = `[${new Date().toISOString()}] ${s}\n`; appendFileSync(LOG, line); process.stdout.write(line); };

function step(name, args, timeoutMs) {
  log(`===== STEP ${name} START: core.py ${args.join(' ')}`);
  const r = spawnSync(PY, ['core.py', ...args], {
    cwd: APPLIO, encoding: 'utf8', timeout: timeoutMs,
    maxBuffer: 64 * 1024 * 1024,
  });
  appendFileSync(LOG, (r.stdout || '') + (r.stderr || ''));
  log(`===== STEP ${name} EXIT=${r.status} signal=${r.signal ?? ''}`);
  if (r.status !== 0) { log(`ABORT: ${name} 非零退出,后续步骤不跑`); process.exit(1); }
}

log('批138 Chris 训练驱动启动(sample-rate=40000, f0=rmvpe, embedder=contentvec, gpu=0)');

step('preprocess', ['preprocess', '--model-name', 'chris', '--dataset-path', DATASET,
  '--sample-rate', '40000', '--cpu-cores', '8'], 3600_000);
// 2026-09-01:Torta 线实撞 8 核 extract 挂死,同修法降 2 核(见 train-torta-driver 头注)。
step('extract', ['extract', '--model-name', 'chris', '--f0-method', 'rmvpe',
  '--cpu-cores', '2', '--gpu', '0', '--sample-rate', '40000', '--embedder-model', 'contentvec'], 7200_000);
step('train', ['train', '--model-name', 'chris', '--vocoder', 'HiFi-GAN',
  '--save-every-epoch', '5', '--save-only-latest', '--total-epoch', '300',
  '--sample-rate', '40000', '--batch-size', '8', '--gpu', '0'], 172800_000);

log('全部步骤完成(train 正常退出)');
