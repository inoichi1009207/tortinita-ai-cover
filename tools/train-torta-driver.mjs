// 批138 条件3 驱动:Applio 串行管线 prerequisites → preprocess → extract → train(Torta)
// 跑法: node train-torta-driver.mjs   (cwd 任意;路径全绝对)
// 日志: D:/test/clipboard/ai-cover/train-torta.log(追加);每步自报口径与退出码
import { spawnSync } from 'node:child_process';
import { appendFileSync } from 'node:fs';

const PY = 'D:/test/clipboard/ai-cover/venv-applio/Scripts/python.exe';
const APPLIO = 'D:/test/clipboard/ai-cover/applio';
const LOG = 'D:/test/clipboard/ai-cover/train-torta.log';
const DATASET = 'D:/test/clipboard/ai-cover/dataset/train/torta';

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

log('批138 Torta 训练驱动启动(sample-rate=40000, f0=rmvpe, embedder=contentvec, gpu=0)');

step('prerequisites', ['prerequisites', '--pretraineds-hifigan', '--models', '--no-exe'], 3600_000);
step('preprocess', ['preprocess', '--model-name', 'torta', '--dataset-path', DATASET,
  '--sample-rate', '40000', '--cpu-cores', '8'], 3600_000);
// 2026-09-01 07:2x 实撞:--cpu-cores 8 的 extract 在 f0 2020/3319 处挂死 29 分钟(GPU 0%),
// Windows 多进程池嫌疑;降 2 核重跑(牺牲并行度换活性),产物目录已隔离重建。
step('extract', ['extract', '--model-name', 'torta', '--f0-method', 'rmvpe',
  '--cpu-cores', '2', '--gpu', '0', '--sample-rate', '40000', '--embedder-model', 'contentvec'], 7200_000);
step('train', ['train', '--model-name', 'torta', '--vocoder', 'HiFi-GAN',
  '--save-every-epoch', '5', '--save-only-latest', '--total-epoch', '300',
  '--sample-rate', '40000', '--batch-size', '8', '--gpu', '0'], 172800_000);

log('全部步骤完成(train 正常退出)');
