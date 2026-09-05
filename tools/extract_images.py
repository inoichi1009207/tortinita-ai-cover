"""从 HyPack 封包按索引直接切出 PNG(EVCG.PAK 立绘/EVBG.PAK 背景都是直存 PNG,comp=0,不需要解码)。
用法(在 clipboard/ai-cover/ 下):venv/Scripts/python.exe tools/extract_images.py <游戏目录> [名字前缀过滤,如 srchr 或 srbg]
产物:pv/assets/sprites/(EVCG)与 pv/assets/bg/(EVBG)。只读游戏目录。"""
import os, struct, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
GAME = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('SR_GAME_DIR', '')
PREFIX = sys.argv[2] if len(sys.argv) > 2 else ''
assert GAME and os.path.isdir(GAME), '给游戏目录(参数 1 或环境变量 SR_GAME_DIR)'
def entries(path):
    b = open(path, 'rb').read(); assert b[:6] == b'HyPack', path
    idx = 0x10 + struct.unpack_from('<I', b, 8)[0]; cnt = struct.unpack_from('<I', b, 12)[0]
    for i in range(cnt):
        r = idx + 48 * i
        name = b[r:r + 0x15].split(b'\0')[0].decode('latin1'); ext = b[r + 0x15:r + 0x18].split(b'\0')[0].decode('latin1')
        off = 0x10 + struct.unpack_from('<I', b, r + 0x18)[0]; packed = struct.unpack_from('<I', b, r + 0x20)[0]; comp = b[r + 0x24]
        yield name, ext, comp, b[off:off + packed]
for pak, out in (('EVCG.PAK', 'pv/assets/sprites'), ('EVBG.PAK', 'pv/assets/bg')):
    os.makedirs(out, exist_ok=True); n = 0
    for name, ext, comp, data in entries(os.path.join(GAME, pak)):
        if ext == 'png' and comp == 0 and name.startswith(PREFIX) and data[:8] == b'\x89PNG\r\n\x1a\n':
            open(os.path.join(out, name + '.png'), 'wb').write(data); n += 1
    print(pak, '->', out, n, '张')
