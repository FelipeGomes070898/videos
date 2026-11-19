import math, random
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
NAVY = (14, 24, 56); BLACK = (5, 7, 14); BEIGE = (228, 214, 186); WH = (246, 244, 238)
GRAY = (150, 156, 168); OR = (206, 100, 40); YL = (244, 214, 130)
FD = '/usr/share/fonts/truetype/google-fonts/'
DV = '/usr/share/fonts/truetype/dejavu/'
_fc = {}


def font(sz, kind='b'):
    k = (sz, kind)
    if k not in _fc:
        p = {'b': FD + 'Poppins-Bold.ttf', 'm': FD + 'Poppins-Medium.ttf', 'mono': DV + 'DejaVuSansMono.ttf', 'monob': DV + 'DejaVuSansMono-Bold.ttf'}[kind]
        _fc[k] = ImageFont.truetype(p, sz)
    return _fc[k]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def E(x):  # ease out cubic
    x = clamp(x)
    return 1 - (1 - x) ** 3


def IO(x):  # ease in-out
    x = clamp(x)
    return x * x * (3 - 2 * x)


def BACK(x):
    x = clamp(x)
    s = 1.70158
    x -= 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


_g = {}


def grad(key, stops):
    if key not in _g:
        ys = np.linspace(0, 1, H)
        pos = [s[0] for s in stops]
        a = np.stack([np.interp(ys, pos, [s[1][c] for s in stops]) for c in range(3)], axis=1)
        _g[key] = np.repeat(a[:, None, :], W, axis=1).astype(np.float32)
    return _g[key].copy()


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def add_glow(a, cx, cy, r, col, k):
    x0, x1 = int(max(0, cx - r)), int(min(W, cx + r))
    y0, y1 = int(max(0, cy - r)), int(min(H, cy + r))
    if x1 <= x0 or y1 <= y0:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    f = np.clip(1 - d, 0, 1) ** 2 * k
    a[y0:y1, x0:x1] += f[..., None] * np.array(col, dtype=np.float32)


def newov():
    o = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    return o, ImageDraw.Draw(o)


def over(img, ov):
    return Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')


class Cam:
    def __init__(self, cx=W / 2, cy=H / 2, z=1.0):
        self.cx, self.cy, self.z = cx, cy, z


class G:
    """Desenho com camera (zoom/pan) aplicada."""
    def __init__(self, d, cam=None):
        self.d = d
        self.c = cam or Cam()

    def P(self, x, y):
        c = self.c
        return ((x - c.cx) * c.z + W / 2, (y - c.cy) * c.z + H / 2)

    def poly(self, pts, fill, outline=None, w=1):
        self.d.polygon([self.P(x, y) for x, y in pts], fill=fill, outline=outline)

    def circ(self, x, y, r, fill=None, outline=None, w=1):
        px, py = self.P(x, y)
        r *= self.c.z
        self.d.ellipse([px - r, py - r, px + r, py + r], fill=fill, outline=outline, width=max(1, int(w * self.c.z)) if outline else 0)

    def ell(self, x0, y0, x1, y1, fill=None, outline=None, w=1):
        a = self.P(x0, y0); b = self.P(x1, y1)
        self.d.ellipse([a[0], a[1], b[0], b[1]], fill=fill, outline=outline, width=max(1, int(w * self.c.z)) if outline else 0)

    def rect(self, x0, y0, x1, y1, fill, r=0):
        a = self.P(x0, y0); b = self.P(x1, y1)
        if r:
            self.d.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=r * self.c.z, fill=fill)
        else:
            self.d.rectangle([a[0], a[1], b[0], b[1]], fill=fill)

    def line(self, pts, fill, w=1):
        self.d.line([self.P(x, y) for x, y in pts], fill=fill, width=max(1, int(w * self.c.z)), joint='curve')


# ------------------------------------------------------------------ estrelas
_stars = None


def stars(img, t, off=(0, 0), appear=1.0, depth=1.0):
    global _stars
    if _stars is None:
        rnd = random.Random(5)
        _stars = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(.4, 1.0), rnd.uniform(0, 6), rnd.random()) for _ in range(320)]
    ov, od = newov()
    for (x, y, z, ph, o) in _stars:
        if o > appear:
            continue
        sx = (x + off[0] * z * depth) % W
        sy = (y + off[1] * z * depth) % H
        tw = 0.65 + 0.35 * math.sin(t * 2 + ph)
        r = 0.8 + 2.2 * z * tw
        al = int(255 * (0.35 + 0.65 * z) * tw)
        col = (255, 244, 224) if o > .5 else (214, 226, 255)
        od.ellipse([sx - r, sy - r, sx + r, sy + r], fill=col + (al,))
    return over(img, ov)


# ------------------------------------------------------------------ Terra procedural
_tex = None
_sph = {}


def _noise(sc, seed, Ht=1024, Wt=2048):
    r = np.random.default_rng(seed).normal(size=(Ht, Wt)).astype(np.float32)
    n = gaussian_filter(r, sc, mode=('nearest', 'wrap'))
    return (n - n.mean()) / n.std()


def earth_tex():
    global _tex
    if _tex is None:
        n = _noise(34, 1) + 0.6 * _noise(14, 2) + 0.35 * _noise(5, 3) + 0.2 * _noise(2, 7)
        n = (n - n.mean()) / n.std()
        Ht, Wt = n.shape
        lat = np.abs(np.linspace(-1, 1, Ht))[:, None] * np.ones((1, Wt))
        ls = np.clip((n - 0.45) / 0.14, 0, 1)
        ls = (ls * ls * (3 - 2 * ls))[..., None]
        ocean = np.stack([20 + 12 * np.clip(n + 1, 0, 2), 58 + 28 * np.clip(n + 1, 0, 2), 120 + 40 * np.clip(n + 1, 0, 2)], axis=2)
        m2 = _noise(16, 4)
        green = np.stack([78 + 20 * m2, 120 + 14 * m2, 78 + 8 * m2], axis=2)
        sand = np.stack([196 + 8 * m2, 170 + 8 * m2, 118 + 6 * m2], axis=2)
        w = np.clip((lat - 0.35) * 3 - m2 * .6, 0, 1)[..., None]
        landc = green * (1 - w) + sand * w * (1 - np.clip((lat - 0.7) * 4, 0, 1)[..., None]) + sand * 0.0
        ice = np.clip((lat - 0.82) * 12, 0, 1)[..., None]
        base = ocean * (1 - ls) + landc * ls
        base = base * (1 - ice) + np.array([236, 240, 246]) * ice
        cl = _noise(26, 5) * .7 + 0.8 * _noise(6, 6) + 0.5 * _noise(2.2, 8)
        ca = np.clip((cl - 0.75) * 1.0, 0, 0.8)
        _tex = (base.astype(np.float32), ca.astype(np.float32))
    return _tex


def sphere_geo(r):
    if r not in _sph:
        m = int(r * 0.22)
        S = 2 * r + 2 * m
        yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
        x = (xx - S / 2) / r
        y = (yy - S / 2) / r
        rr2 = x * x + y * y
        inside = rr2 < 1
        z = np.sqrt(np.clip(1 - rr2, 0, 1))
        lon = np.arctan2(x, z)
        lat = np.arcsin(np.clip(-y, -1, 1))
        u0 = ((lon / (2 * math.pi) + 0.5) * 2048).astype(np.float32)
        v = np.clip(((lat / math.pi) + 0.5) * 1023, 0, 1023).astype(np.int32)
        L = np.array([-0.5, -0.42, 0.75]); L /= np.linalg.norm(L)
        sh = np.clip(x * L[0] + y * L[1] + z * L[2], 0, 1)
        d = np.sqrt(rr2)
        _sph[r] = dict(S=S, m=m, inside=inside, z=z, u0=u0, v=v, sh=sh, d=d)
    return _sph[r]


def earth_sprite(r, shift):
    """Retorna RGBA (S,S) da Terra com atmosfera. shift = rotacao em pixels de textura."""
    base, ca = earth_tex()
    g = sphere_geo(r)
    u = ((g['u0'] + shift * 2).astype(np.int32)) % 2048
    uc = ((g['u0'] + shift * 2.7).astype(np.int32)) % 2048
    col = base[g['v'], u]
    cloud = ca[g['v'], uc][..., None]
    col = col * (1 - cloud) + 245 * cloud
    sh = (0.10 + 0.95 * g['sh'] ** 0.9)[..., None]
    col = col * sh
    rim = ((1 - g['z']) ** 2.4)[..., None] * np.array([70, 140, 255]) * (0.35 + 0.8 * g['sh'][..., None])
    col = col + rim
    # brilho de cidades no lado escuro
    a = np.zeros(col.shape[:2], np.float32)
    a[g['inside']] = 255
    # halo atmosferico
    d = g['d']
    halo = np.exp(-np.clip(d - 1, 0, 1) * 18) * (d >= 1) * (d < 1.22)
    hcol = np.array([90, 160, 255], np.float32)
    out = np.zeros(col.shape[:2] + (4,), np.float32)
    out[..., :3] = np.where(g['inside'][..., None], col, hcol)
    out[..., 3] = np.where(g['inside'], 255, halo * 150)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')


def paste_center(img, sprite, cx, cy, scale=1.0, alpha=1.0):
    if scale != 1.0:
        sprite = sprite.resize((max(2, int(sprite.width * scale)), max(2, int(sprite.height * scale))), Image.BILINEAR)
    if alpha < 1.0:
        a = sprite.split()[3].point(lambda v: int(v * alpha))
        sprite = sprite.copy(); sprite.putalpha(a)
    img = img.convert('RGBA')
    img.alpha_composite(sprite, (int(cx - sprite.width / 2), int(cy - sprite.height / 2))) if (cx - sprite.width / 2) >= 0 and (cy - sprite.height / 2) >= 0 else img.paste(sprite, (int(cx - sprite.width / 2), int(cy - sprite.height / 2)), sprite)
    return img.convert('RGB')


def earth(img, cx, cy, R, t, base_r=560, spin=26):
    sp = earth_sprite(base_r, t * spin)
    scale = R / base_r
    return paste_center(img, sp, cx, cy, scale)


_moon = {}


def moon_sprite(r):
    if r not in _moon:
        g = sphere_geo(r)
        n = _noise(30, 11) * .5 + _noise(10, 12) * .25
        base = 168 + 26 * n
        mare = np.clip(_noise(40, 13) - 0.2, 0, 1) * 55
        gray = base - mare
        u = (g['u0'].astype(np.int32)) % 2048
        val = gray[g['v'], u]
        rnd = np.random.default_rng(4)
        sh = (0.08 + 1.0 * g['sh'] ** 0.85)
        col = np.stack([val * 1.0, val * 0.99, val * 0.95], axis=2) * sh[..., None]
        S = g['S']
        out = np.zeros((S, S, 4), np.float32)
        out[..., :3] = col
        out[..., 3] = np.where(g['inside'], 255, 0)
        im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')
        dd = ImageDraw.Draw(im)
        for i in range(26):
            a = rnd.uniform(0, 6.283); rr = math.sqrt(rnd.uniform(0, .85)) * r
            cx = S / 2 + rr * math.cos(a); cy = S / 2 + rr * math.sin(a)
            cr = rnd.uniform(.03, .1) * r
            dd.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], outline=(90, 90, 94, 120), width=max(1, int(r * .012)))
        _moon[r] = im
    return _moon[r]


def moon(img, cx, cy, R, base_r=200):
    return paste_center(img, moon_sprite(base_r), cx, cy, R / base_r)


# ------------------------------------------------------------------ texto
def txt(d, xy, s, sz, fill, anchor='la', kind='b'):
    d.text(xy, s, font=font(sz, kind), fill=fill, anchor=anchor)


def glowtext(img, xy, s, sz, fill, anchor='mm', kind='b', k=0.8):
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.text(xy, s, font=font(sz, kind), fill=fill + (255,), anchor=anchor)
    gl = ov.filter(ImageFilter.GaussianBlur(14))
    a = gl.split()[3].point(lambda v: int(v * k))
    gl.putalpha(a)
    img = Image.alpha_composite(img.convert('RGBA'), gl)
    return Image.alpha_composite(img, ov).convert('RGB')


# ------------------------------------------------------------------ personagens
def silhouette(g, x, y, s, sway=0.0, col=(8, 10, 16)):
    """pessoa em silhueta, y = pes, s = altura"""
    hx = x + sway * s * .02
    g.poly([(hx - .16 * s, y - .62 * s), (hx + .16 * s, y - .62 * s), (hx + .13 * s, y - .28 * s), (x + .1 * s, y), (x - .1 * s, y), (hx - .13 * s, y - .28 * s)], col)
    g.rect(x - .12 * s, y - .02 * s, x - .02 * s, y, col)
    g.circ(hx, y - .75 * s, .11 * s, col)
    g.poly([(hx - .16 * s, y - .6 * s), (hx - .26 * s, y - .35 * s), (hx - .2 * s, y - .33 * s), (hx - .12 * s, y - .5 * s)], col)
    g.poly([(hx + .16 * s, y - .6 * s), (hx + .26 * s, y - .35 * s), (hx + .2 * s, y - .33 * s), (hx + .12 * s, y - .5 * s)], col)


def astronaut(g, x, y, s, ph=0.0, arm=0.0, face=1, dark=0.0, visor=True):
    """astronauta em traje branco; y = pes; s = altura em px"""
    f = face
    wc = mix((236, 236, 240), (90, 92, 110), dark)
    sc = mix((200, 202, 210), (60, 62, 78), dark)
    sw = math.sin(ph)
    for sg in (1, -1):
        lx = x + sg * .07 * s
        fx = lx + sw * sg * .09 * s * f
        g.poly([(lx - .06 * s, y - .42 * s), (lx + .06 * s, y - .42 * s), (fx + .06 * s, y - .04 * s), (fx - .06 * s, y - .04 * s)], wc if sg == 1 else sc)
        g.rect(fx - .08 * s + .03 * s * f, y - .05 * s, fx + .08 * s + .03 * s * f, y, (84, 86, 92))
    g.rect(x - .22 * s * (1 if f == 1 else 1) - (.12 * s if f == 1 else -.0), y - .72 * s, x - .1 * s * f - (.12 * s if f == 1 else -.0) + .0, y - .3 * s, sc, r=int(.05 * s))
    g.rect(x - .13 * s, y - .72 * s, x + .13 * s, y - .36 * s, wc, r=int(.06 * s))
    for sg in (1, -1):
        ax = x + sg * .14 * s
        g.poly([(ax - .04 * s, y - .68 * s), (ax + .04 * s, y - .68 * s), (ax + sg * .08 * s + math.sin(arm + sg) * .05 * s * f, y - .42 * s), (ax + sg * .02 * s + math.sin(arm + sg) * .05 * s * f, y - .42 * s)], wc if sg == f else sc)
    g.circ(x, y - .82 * s, .12 * s, wc)
    if visor:
        g.circ(x + .02 * s * f, y - .82 * s, .085 * s, (228, 176, 70))
        g.circ(x + .0 * s * f - .02 * s, y - .85 * s, .03 * s, (255, 238, 190))
