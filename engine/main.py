import sys, os, json, math, subprocess
import numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFilter
from common import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO_DIR = os.environ.get('VIDEO_DIR', os.path.join(ROOT, 'scenes', 'corrida_espacial'))
sys.path.insert(0, VIDEO_DIR)
import scenes as SC
OUT_DIR = os.environ.get('OUT_DIR', os.path.join(ROOT, 'out'))
os.makedirs(OUT_DIR, exist_ok=True)
SUBTITLES = os.environ.get('SUBS', '0') == '1'   # padrao: sem legenda queimada

PARAMS = json.load(open(os.path.join(VIDEO_DIR, 'params.json')))
DUR = json.load(open(os.path.join(VIDEO_DIR, 'dur.json')))
NOFF = PARAMS['narr_offsets']
NARR = PARAMS['narracao']
TR = PARAMS['transition_s']
TRANS = {int(k): (v[0], tuple(v[1]) if v[1] else None, v[2] if len(v) > 2 else 'up') for k, v in PARAMS['transitions'].items()}


def chunks(text, maxc=30):
    words = text.split()
    lines, cur = [], ''
    for w in words:
        if len(cur) + len(w) + 1 > maxc and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + ' ' + w).strip()
    lines.append(cur)
    out = []
    for i in range(0, len(lines), 2):
        out.append(lines[i:i + 2])
    return out


SUBS = []
for i, tx in enumerate(NARR):
    st = SC.STARTS[i] + NOFF[i]
    ch = chunks(tx)
    tot = sum(len(' '.join(c)) for c in ch)
    cur = st
    for c in ch:
        L = len(' '.join(c)) / tot * DUR[i]
        SUBS.append((cur, cur + L, c))
        cur += L

VIG = None
PAPER = None


def sub_layer(img, t):
    for a, b, lines in SUBS:
        if a - .05 <= t < b + .15:
            al = clamp((t - a) / .25) * clamp((b + .15 - t) / .25)
            ov, od = newov()
            od.rectangle([0, 1620, W, H], fill=(3, 5, 12, int(120 * al)))
            img = over(img, ov)
            lay = Image.new('RGBA', (W, 300), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            f = font(50, 'b')
            y0 = 150 - len(lines) * 36
            for j, ln in enumerate(lines):
                d.text((W / 2 + 3, y0 + j * 72 + 3), ln, font=f, fill=(0, 0, 0, int(160 * al)), anchor='ma')
                d.text((W / 2, y0 + j * 72), ln, font=f, fill=(246, 244, 238, int(255 * al)), anchor='ma')
            img = img.convert('RGBA')
            img.alpha_composite(lay, (0, int(1640 + 8 * (1 - al))))
            return img.convert('RGB')
    return img


def bloom(a, k=0.35, thr=170):
    a = _bloom(a, k, thr)
    if ORIENT == 'h':
        sm = np.asarray(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((W // 8, H // 8), Image.BILINEAR)).astype(np.float32)
        br = np.clip((sm - 215) * 3.0, 0, 255)
        from scipy.ndimage import uniform_filter1d
        br = uniform_filter1d(br, 40, axis=1)
        st = np.asarray(Image.fromarray(np.clip(br, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32)
        a = a + st * np.array([.18, .26, .38], np.float32)
    return a


def _bloom(a, k=0.35, thr=170):
    sm = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
    s = np.asarray(sm).astype(np.float32)
    br = np.clip((s - thr) * 1.8, 0, 255)
    bi = Image.fromarray(br.astype(np.uint8)).filter(ImageFilter.GaussianBlur(8)).resize((W, H), Image.BICUBIC)
    return a + np.asarray(bi).astype(np.float32) * k


def iris(A, B, c, u):
    cx, cy = c
    R = IO(u) * 1.35 * math.hypot(W, H)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    m = np.clip((R - d) / 36 + .5, 0, 1)[..., None]
    out = np.asarray(B).astype(np.float32) * m + np.asarray(A).astype(np.float32) * (1 - m)
    ring = np.clip(1 - np.abs(d - R) / 7, 0, 1)[..., None] * np.array([244, 190, 90], np.float32) * (1 - u * .6)
    return to_img(out + ring)


def wipe(A, B, u, up=True):
    ue = IO(u)
    ys = np.arange(H, dtype=np.float32)[:, None, None]
    edge = H * (1 - ue) if up else H * ue
    m = np.clip(((ys - edge) / 60.0 + .5) if up else ((edge - ys) / 60.0 + .5), 0, 1)
    m = np.broadcast_to(m, (H, W, 1))
    out = np.asarray(B).astype(np.float32) * m + np.asarray(A).astype(np.float32) * (1 - m)
    ring = np.clip(1 - np.abs(ys - edge) / 6, 0, 1) * np.array([244, 190, 90], np.float32)
    return to_img(out + ring)


def hwipe(A, B, u):
    ue = IO(u)
    xs = np.arange(W, dtype=np.float32)[None, :, None]
    edge = W * ue
    mk = np.clip((edge - xs) / 80.0 + .5, 0, 1)
    mk = np.broadcast_to(mk, (H, W, 1))
    out = np.asarray(B).astype(np.float32) * mk + np.asarray(A).astype(np.float32) * (1 - mk)
    ring = np.clip(1 - np.abs(xs - edge) / 6, 0, 1) * np.array([244, 190, 90], np.float32)
    return to_img(out + ring)


def zoomx(A, B, u):
    ue = IO(u)
    za = 1 + 0.55 * ue
    zb = 1.35 - 0.35 * ue
    def zm(im, z):
        a = 1 / z
        return im.transform((W, H), Image.AFFINE, (a, 0, W / 2 * (1 - a), 0, a, H / 2 * (1 - a)), resample=Image.BILINEAR)
    return Image.blend(zm(A, za), zm(B, zb), ue)


GRADE = [(1.05, 1.0, .95), (.97, 1.0, 1.06), (.98, 1.0, 1.04), (1.04, 1.0, .94), (1.04, 1.0, .96), (1.0, 1.0, 1.0), (1.02, 1.0, .98), (1.0, 1.0, 1.02)]


def frame(i):
    global VIG, PAPER
    t = i / FPS
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]
        dd = np.sqrt(((xx - W / 2) / (W * .74)) ** 2 + ((yy - H / 2) / (H * .74)) ** 2)
        VIG = (1 - 0.34 * np.clip(dd, 0, 1) ** 2)[..., None].astype(np.float32)
        pn = gaussian_filter(np.random.default_rng(1).normal(size=(H // 2, W // 2)).astype(np.float32), 1.2)
        pn = np.asarray(Image.fromarray(((pn - pn.min()) / (pn.max() - pn.min()) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
        PAPER = (0.965 + 0.05 * pn)[..., None]
    NS = len(SC.STARTS)
    idx = max(k for k in range(NS) if SC.STARTS[k] <= t + 1e-6)
    gi = idx
    img = None
    for k in range(1, NS):
        b = SC.STARTS[k]
        if b - TR / 2 <= t < b + TR / 2:
            u = (t - (b - TR / 2)) / TR
            A = SC.SCENES[k - 1](t - SC.STARTS[k - 1])
            B = SC.SCENES[k](max(0, t - b))
            typ, c, dr = TRANS[k]
            if typ == 'iris':
                img = iris(A, B, c, u)
            elif typ == 'wipe':
                img = wipe(A, B, u, up=(dr == 'up'))
            elif typ == 'hwipe':
                img = hwipe(A, B, u)
            else:
                img = zoomx(A, B, u)
            gi = k - 1 if u < .5 else k
    if img is None:
        img = SC.SCENES[idx](t - SC.STARTS[idx])
    a = np.asarray(img).astype(np.float32)
    a = bloom(a)
    a = a * np.array(GRADE[gi % len(GRADE)], np.float32)
    a = (a - 128) * 1.07 + 128
    img = to_img(a)
    if SUBTITLES:
        img = sub_layer(img, t)
    a = np.asarray(img).astype(np.float32) * VIG * PAPER
    rng = np.random.default_rng(i)
    a = a + rng.normal(0, 2.6, (H, W, 1)).astype(np.float32)
    # fade in/out
    f = clamp(t / .6) * clamp((SC.TOTAL - t) / 1.0)
    a = a * f
    return np.clip(a, 0, 255).astype(np.uint8).tobytes()


def main():
    if sys.argv[1] == 'still':
        for ts in sys.argv[2].split(','):
            Image.frombytes('RGB', (W, H), frame(int(float(ts) * FPS))).save(os.path.join(OUT_DIR, 'still_' + ts + '.png'))
        return
    out1080, out4k = sys.argv[1], sys.argv[2]
    n = int(SC.TOTAL * FPS)
    cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-filter_complex', '[0:v]split=2[a][b];[b]scale=%d:%d:flags=lanczos[c]' % tuple(PARAMS.get('resolucao_final', [2160, 3840])),
           '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out1080,
           '-map', '[c]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', out4k]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(2) as p:
        for j, fr in enumerate(p.imap(frame, range(n), chunksize=3)):
            ff.stdin.write(fr)
            if j % 120 == 0:
                print(j, '/', n, flush=True)
    ff.stdin.close()
    ff.wait()


if __name__ == '__main__':
    main()
