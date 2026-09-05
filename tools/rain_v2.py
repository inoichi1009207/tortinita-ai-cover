"""PV rain v2; run: venv/Scripts/python.exe tools/rain_v2.py.

All asset paths are relative to clipboard/ai-cover (resolved from this file).
Default consumer: build_pv9_rain_v2.py builds assets before loading its textures.
Retire/retrace when backgrounds or the fixed 1920x1080 framing change.
Usage counter and source/output hashes: pv/assets/masks/rain_v2_metrics.json.
Only numpy and Pillow are required. Source PNG alpha is deliberately ignored.
"""
from pathlib import Path
import hashlib
import json
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
W, H = 1920, 1080
RAIN_FPS = 8
STEP_Y = 57
SLOPE = math.tan(math.radians(-6))  # degrees from downward vertical; leftward

# Hand traced in ORIGINAL 640x480 coordinates; scale x by 3, y by 2.25.
# Each polygon is a single visible pane, already inside frame/arch boundaries.
# No brightness, saturation, original alpha, or sky classification is used.
PANES = {
    'srbg054': [
        [(0, 0), (54, 0), (54, 98), (0, 88)],
        [(68, 0), (131, 0), (133, 112), (68, 101)],
        [(147, 10), (163, 23), (180, 44), (193, 66), (204, 91), (211, 123), (147, 114)],
        [(0, 114), (132, 138), (133, 370), (0, 370)],
        [(148, 142), (213, 151), (214, 370), (148, 370)],
        [(300, 141), (303, 125), (310, 108), (319, 95), (329, 83), (336, 77), (336, 147)],
        [(300, 166), (336, 172), (336, 370), (300, 370)],
        [(396, 76), (410, 81), (423, 90), (423, 167), (396, 163)],
        [(435, 102), (447, 116), (459, 136), (467, 156), (471, 172), (435, 169)],
        [(386, 180), (424, 186), (424, 370), (386, 370)],
        [(436, 190), (471, 195), (471, 369), (436, 370)],
    ],
    'srbg026': [
        [(0, 0), (14, 0), (14, 27), (0, 18)],
        [(24, 0), (74, 0), (130, 40), (130, 95), (24, 25)],
        [(84, 0), (129, 0), (129, 32)],
        [(140, 6), (151, 28), (162, 57), (170, 86), (172, 97), (140, 76)],
        [(140, 86), (171, 106), (172, 125), (140, 104)],
        [(0, 31), (14, 41), (14, 241), (0, 238)],
        [(25, 45), (78, 80), (78, 253), (25, 241)],
        [(88, 87), (131, 116), (131, 265), (88, 255)],
        [(141, 121), (172, 141), (172, 273), (141, 266)],
        [(0, 251), (14, 254), (14, 350), (0, 350)],
        [(25, 257), (78, 268), (78, 350), (25, 350)],
        [(88, 270), (131, 279), (131, 350), (88, 350)],
        [(141, 282), (172, 288), (172, 350), (141, 350)],
        [(228, 113), (234, 102), (242, 95), (243, 138), (228, 129)],
        [(251, 92), (257, 92), (264, 96), (264, 140), (251, 132)],
        [(273, 108), (279, 120), (282, 133), (282, 157), (273, 150)],
        [(289, 151), (296, 176), (298, 189), (289, 183)],
        [(228, 143), (242, 151), (242, 170), (228, 162)],
        [(251, 145), (282, 166), (282, 191), (251, 173)],
        [(228, 177), (242, 185), (242, 292), (228, 289)],
        [(251, 190), (263, 197), (263, 296), (251, 293)],
        [(272, 202), (282, 208), (282, 299), (272, 297)],
        [(290, 212), (299, 217), (300, 304), (290, 301)],
        [(228, 302), (242, 305), (242, 350), (228, 351)],
        [(251, 307), (263, 309), (263, 350), (251, 350)],
        [(272, 311), (282, 313), (282, 350), (272, 350)],
        [(290, 315), (300, 317), (300, 350), (290, 350)],
        # Third arch's tiny upper panes omitted: diagonal bars are ambiguous.
        [(324, 226), (330, 230), (330, 310), (324, 309)],
        [(338, 235), (343, 238), (343, 313), (338, 312)],
        [(350, 242), (355, 245), (355, 316), (350, 315)],
        [(361, 250), (363, 252), (364, 318), (361, 318)],
        [(324, 319), (330, 320), (330, 352), (324, 353)],
        [(338, 322), (343, 323), (343, 351), (338, 352)],
        [(350, 325), (355, 326), (355, 350), (350, 351)],
        # Far windows beyond x=367 are conservatively omitted (tiny bars/plant).
    ],
    'srbg296': [
        [(94, 53), (95, 53), (95, 109), (85, 109)],
        [(104, 53), (141, 53), (142, 109), (104, 109)],
        [(154, 53), (192, 53), (192, 109), (154, 109)],
        [(202, 52), (235, 52), (235, 109), (202, 109)],
        [(264, 53), (298, 53), (299, 109), (264, 109)],
        [(307, 51), (342, 48), (343, 109), (307, 109)],
        [(354, 50), (388, 50), (388, 108), (354, 108)],
        [(84, 118), (95, 118), (95, 176), (75, 176)],
        [(105, 119), (142, 119), (143, 176), (105, 176)],
        [(155, 119), (192, 119), (192, 176), (155, 176)],
        [(202, 119), (235, 119), (235, 176), (202, 176)],
        [(264, 119), (298, 119), (298, 176), (264, 176)],
        [(308, 119), (343, 119), (344, 176), (308, 176)],
        [(354, 119), (388, 119), (388, 175), (354, 175)],
        [(400, 119), (404, 119), (411, 154), (414, 174), (400, 175)],
        [(73, 186), (96, 186), (97, 235), (73, 235), (70, 224), (74, 200)],
        [(106, 186), (143, 186), (144, 235), (106, 235)],
        [(155, 186), (192, 186), (192, 235), (155, 235)],
        [(202, 186), (235, 186), (235, 235), (202, 235)],
        [(264, 186), (298, 186), (299, 235), (264, 235)],
        [(308, 186), (344, 186), (344, 235), (308, 235)],
        [(354, 186), (388, 185), (388, 235), (354, 235)],
        [(400, 185), (416, 185), (416, 193), (413, 210), (412, 235), (400, 235)],
        [(76, 246), (97, 246), (98, 298), (84, 298)],
        [(107, 246), (144, 246), (144, 298), (107, 298)],
        [(156, 246), (191, 246), (191, 298), (156, 298)],
        [(202, 246), (235, 246), (235, 255), (214, 255), (210, 268), (207, 298), (202, 298)],
        [(264, 246), (298, 246), (298, 267), (283, 271), (272, 273), (267, 281), (264, 281)],
        [(308, 246), (343, 246), (343, 298), (324, 298), (323, 280), (315, 270), (308, 267)],
        [(355, 246), (388, 246), (388, 282), (355, 282)],
        [(400, 246), (411, 246), (406, 298), (400, 298)],
    ],
    'srbg266': [
        [(0, 59), (22, 64), (22, 98), (0, 95)],
        [(42, 67), (82, 77), (82, 110), (42, 103)],
        [(0, 113), (22, 116), (22, 154), (0, 152)],
        [(42, 121), (82, 128), (82, 161), (42, 158)],
        [(0, 168), (22, 170), (22, 212), (0, 213)],
        [(42, 174), (82, 176), (82, 215), (42, 214)],
        [(0, 230), (22, 230), (22, 275), (0, 277)],
        [(42, 230), (82, 230), (82, 270), (42, 275)],
    ],
}

# Independent hand-picked pixels: dark/cloud glass must survive, objects must not.
PROBES = {
    'srbg054': {'zero': [(360, 80), (360, 260), (140, 200), (100, 399), (480, 300)],
                'glass': [(30, 40), (100, 70), (180, 190), (320, 220), (451, 240)]},
    'srbg026': {'zero': [(160, 12), (240, 50), (290, 120), (310, 150), (210, 280), (82, 220)],
                'glass': [(45, 140), (110, 225), (156, 320), (255, 250), (294, 275)]},
    'srbg296': {'zero': [(248, 200), (149, 200), (120, 240), (223, 278), (298, 289), (365, 295), (420, 130)],
                'glass': [(125, 80), (174, 145), (220, 211), (283, 151), (373, 264)]},
    'srbg266': {'zero': [(31, 180), (62, 221), (104, 200), (140, 150)],
                'glass': [(12, 80), (60, 90), (60, 142), (60, 195), (60, 250)]},
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pane_mask(name):
    hard = Image.new('L', (W, H))
    draw = ImageDraw.Draw(hard)
    for polygon in PANES[name]:
        draw.polygon([(round(x * 3), round(y * 2.25)) for x, y in polygon], fill=255)
    # Three inward 1px steps: outside=0; edge=0,85,170; core=255.
    # Unlike a Gaussian, this cannot leak onto excluded objects.
    levels = [np.asarray(hard.filter(ImageFilter.MinFilter(k)), dtype=np.uint16)
              for k in (3, 5, 7)]
    soft = (sum(levels) // 3).astype(np.uint8)
    assert not np.any(soft[np.asarray(hard) == 0])
    for kind, points in PROBES[name].items():
        for x, y in points:
            value = int(soft[round(y * 2.25), round(x * 3)])
            assert value == (0 if kind == 'zero' else 255), (name, kind, x, y, value)
    if name == 'srbg054':
        assert not soft[:, 1010:1151].any()
        assert not soft[840:].any()
    return Image.fromarray(soft)


def offset(frame):
    dy = round(frame * STEP_Y)
    return round(frame * STEP_Y * SLOPE), dy


def rain_at(frames, t):
    """30fps continuous advection; compensate baked phase including each 8->1 wrap.

    The eight PNGs alone are still periodic. The consumer must use this function
    rather than simply frames[int(t*8)%8]. Mask only AFTER translating the rain.
    """
    phase = t * RAIN_FPS
    k = math.floor(phase) % 8
    bx, by = offset(k)
    tx, ty = offset(phase)
    return np.roll(frames[k], (ty - by, tx - bx), axis=(0, 1))


def rain_base():
    rng = np.random.default_rng(20260905)
    base = np.zeros((H, W), dtype=np.uint8)
    statistics = []
    # One streak per cell per layer. Keep uniformity without a visible lattice.
    for cw, ch, lo, hi, width in [(80, 90, 45, 80, 1), (120, 135, 80, 110, 2)]:
        hi_res = Image.new('L', (W * 2, H * 2))
        draw = ImageDraw.Draw(hi_res)
        points = []
        for row in range(H // ch):
            for col in range(W // cw):
                x = (col + rng.uniform(.12, .88)) * cw
                y = (row + rng.uniform(.12, .88)) * ch
                length = rng.uniform(lo, hi)
                angle = rng.uniform(-8, -4)
                alpha = rng.uniform(.35, .75)
                dx = length * math.sin(math.radians(angle))
                dy = length * math.cos(math.radians(angle))
                points.append((x, y, length, angle, alpha))
                # Wrap BOTH endpoints using translated copies of the same line.
                for ox in (-W, 0, W):
                    for oy in (-H, 0, H):
                        draw.line((round((x + ox) * 2), round((y + oy) * 2),
                                   round((x + ox + dx) * 2), round((y + oy + dy) * 2)),
                                  fill=round(alpha * 255), width=width * 2)
        layer = np.asarray(hi_res.resize((W, H), Image.Resampling.BOX))
        base = np.maximum(base, layer)
        cells = {(int(x // cw), int(y // ch)) for x, y, *_ in points}
        assert len(cells) == len(points) == (W // cw) * (H // ch)
        a = np.asarray(points)
        statistics.append({'cell': [cw, ch], 'count': len(points), 'width': width,
                           'length_range': [float(a[:, 2].min()), float(a[:, 2].max())],
                           'angle_range': [float(a[:, 3].min()), float(a[:, 3].max())],
                           'core_alpha_range': [float(a[:, 4].min()), float(a[:, 4].max())]})
    return base, statistics


def build_assets():
    mask_dir = ROOT / 'pv/assets/masks'
    rain_dir = ROOT / 'pv/assets/rain'
    mask_dir.mkdir(parents=True, exist_ok=True)
    rain_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = mask_dir / 'rain_v2_metrics.json'
    previous = json.loads(metrics_path.read_text(encoding='utf-8')) if metrics_path.exists() else {}
    metrics = {'runs': previous.get('runs', 0) + 1, 'masks': {}, 'rain': {},
               'script_sha256': sha256(Path(__file__)), 'outputs': {}}
    for name in PANES:
        source = ROOT / f'pv/assets/bg_all/{name}.png'
        with Image.open(source) as src:
            if src.size != (640, 480):
                raise ValueError(f'{name}: background framing changed; retrace polygons')
            bg = src.convert('RGB').resize((W, H), Image.Resampling.LANCZOS)
        mask = pane_mask(name)
        mask.save(mask_dir / f'{name}.png')
        a = np.asarray(mask)
        preview_alpha = Image.fromarray((a.astype(np.float32) * .48).astype(np.uint8))
        preview = Image.composite(Image.new('RGB', (W, H), (255, 0, 0)), bg, preview_alpha)
        preview.save(mask_dir / f'{name}_preview.jpg', quality=94, subsampling=0)
        with Image.open(mask_dir / f'{name}.png') as check:
            assert check.mode == 'L' and check.size == (W, H)
            assert np.array_equal(np.asarray(check), a)
        metrics['masks'][name] = {
            'coverage_nonzero_pct': round(float(np.mean(a > 0) * 100), 4),
            'coverage_core_pct': round(float(np.mean(a == 255) * 100), 4),
            'coverage_weighted_pct': round(float(a.mean() / 255 * 100), 4),
            'panes': len(PANES[name]), 'background_sha256': sha256(source)}
    base, layers = rain_base()
    frames = []
    for k in range(8):
        dx, dy = offset(k)
        alpha = np.roll(base, (dy, dx), axis=(0, 1))
        rgba = Image.new('RGBA', (W, H), (255, 255, 255, 0))
        rgba.putalpha(Image.fromarray(alpha))
        path = rain_dir / f'streak8_{k + 1}.png'
        rgba.save(path)
        with Image.open(path) as check:
            assert check.mode == 'RGBA' and check.size == (W, H)
            frames.append(np.asarray(check)[..., 3].copy())
        assert np.array_equal(frames[-1], alpha)
    assert len({hashlib.sha256(f.tobytes()).hexdigest() for f in frames}) == 8
    # Include the phase seam, a later cycle, and fractional output-frame times.
    for t in (0, 1/30, 7/8, 29/30, 1, 31/30, 15, 50, 65, 218.8):
        dx, dy = offset(t * RAIN_FPS)
        assert np.array_equal(rain_at(frames, t), np.roll(base, (dy, dx), axis=(0, 1)))
    assert not np.array_equal(rain_at(frames, 0), rain_at(frames, 1))
    metrics['rain'] = {'frames': 8, 'layers': layers, 'total_streaks': sum(x['count'] for x in layers),
                       'alpha_support_pct': round(float(np.mean(base > 0) * 100), 4),
                       'motion_px_per_second': [STEP_Y * RAIN_FPS * SLOPE, STEP_Y * RAIN_FPS],
                       'phase_seam_test': 'PASS', 'one_second_repeat': False}
    for path in ([mask_dir / f'{n}{s}' for n in PANES for s in ('.png', '_preview.jpg')]
                 + [rain_dir / f'streak8_{k}.png' for k in range(1, 9)]):
        metrics['outputs'][path.relative_to(ROOT).as_posix()] = sha256(path)
    metrics_path.write_text(json.dumps(metrics, indent=2) + '\n', encoding='utf-8')
    assert json.loads(metrics_path.read_text(encoding='utf-8')) == metrics
    return metrics


if __name__ == '__main__':
    result = build_assets()
    print(json.dumps({'masks': result['masks'], 'rain': result['rain']}, indent=2))
    print('PASS: disk roundtrip, object/glass probes, stratification, eight phases, motion seam.')
    print('CEILING: geometric probes do not certify every boundary; inspect red previews. '
          'No mathematical test can certify that a viewer will never notice repetition.')
