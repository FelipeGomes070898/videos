"""A Corrida Espacial - versao horizontal 16:9 (1920x1080, 24 fps), 13 cenas. Rodar com ORIENT=h."""
import os, sys, json, math, random, importlib.util
from common import *

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('vscenes', os.path.join(HERE, '..', 'corrida_espacial', 'scenes.py'))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

P = json.load(open(os.path.join(HERE, 'params.json')))
D = json.load(open(os.path.join(HERE, 'dur.json')))
OFF = P['narr_offsets']
TAIL = 0.9
DURS = [OFF[i] + D[i] + TAIL for i in range(len(D))]
DURS[7] = max(DURS[7], 8.0)
DURS[12] += 2.8
STARTS = [sum(DURS[:i]) for i in range(len(DURS))]
TOTAL = sum(DURS)
CX, CY = W / 2, H / 2


def bg(key, stops):
    return to_img(grad(key, stops))


def tx(d, xy, s, sz, col, anchor='la', kind='b'):
    d.text(xy, s, font=font(sz, kind), fill=col, anchor=anchor)


def fadec(t0, dur=.8, c0=BLACK, c1=WH):
    return mix(c0, c1, E(0 if dur == 0 else 0))


def fc(t, t0, c1, c0=BLACK, dur=.8):
    return mix(c0, c1, E((t - t0) / dur))


def sat(od, x, y, sk):
    od.rectangle([x - 22 * sk, y - 12 * sk, x + 22 * sk, y + 12 * sk], fill=(224, 224, 232, 255))
    od.rectangle([x - 22 * sk, y - 12 * sk, x + 22 * sk, y - 5 * sk], fill=(206, 100, 40, 255))
    for sg in (-1, 1):
        xa, xb = sorted((x + sg * 28 * sk, x + sg * 90 * sk))
        od.rectangle([xa, y - 9 * sk, xb, y + 9 * sk], fill=(30, 60, 130, 255), outline=(190, 208, 244, 255), width=2)
        for q in range(1, 4):
            xx = x + sg * (28 + q * 15.5) * sk
            od.line([xx, y - 9 * sk, xx, y + 9 * sk], fill=(190, 208, 244, 230), width=2)
    od.line([x, y - 12 * sk, x, y - 38 * sk], fill=(224, 224, 232, 255), width=4)
    od.ellipse([x - 7, y - 38 * sk - 7, x + 7, y - 38 * sk + 7], fill=(244, 214, 130, 255))


def csm(g, x, y, s, ang=0.0, flame=0.0, t=0.0):
    """modulo de comando e servico. Aponta para a direita (ang=0). s = escala"""
    ca, sa = math.cos(ang), math.sin(ang)
    def R(px, py):
        return (x + (px * ca - py * sa) * s, y + (px * sa + py * ca) * s)
    g.poly([R(-110, -26), R(40, -26), R(40, 26), R(-110, 26)], (210, 212, 220))
    g.poly([R(-110, 8), R(40, 8), R(40, 26), R(-110, 26)], (160, 164, 176))
    g.poly([R(-110, -26), R(-110, 26), R(-130, 18), R(-130, -18)], (80, 84, 96))
    g.poly([R(-130, -12), R(-130, 12), R(-172, 28), R(-172, -28)], (60, 62, 72))
    g.poly([R(40, -26), R(40, 26), R(92, 8), R(92, -8)], (236, 236, 242))
    g.poly([R(40, 6), R(40, 26), R(92, 8), R(92, 4)], (190, 192, 204))
    g.poly([R(-60, -26), R(-48, -26), R(-48, -30), R(-60, -30)], (206, 100, 40))
    g.line([R(-20, -26), R(-4, -50)], (220, 222, 230), max(2, int(2 * s)))
    if flame > 0:
        L = 90 * flame * (1 + .1 * math.sin(t * 40))
        g.poly([R(-172, -22), R(-172, 22), R(-172 - L, 0)], (244, 190, 90))


# ============================================================ 1  Abertura / Guerra Fria
def h1(t):
    d_ = DURS[0]; p = clamp(t / d_)
    img = stars(bg('h1', [(0, BLACK), (.6, (8, 12, 30)), (1, (16, 26, 60))]), t, off=(t * 5, 0), appear=E(t / 5))
    R = lerp(980, 1300, IO(p)); cy = lerp(1480, 1560, IO(p))
    img = earth(img, 960, cy, R, t, spin=24)
    ov, od = newov()
    ts = clamp((t - 1.5) / (d_ * .6))
    def sp(u):
        return (lerp(-260, 2160, u), lerp(760, 300, u) + 55 * math.sin(u * 3.0))
    n = 60
    for i in range(n):
        u = ts - (n - i) * .005
        if u <= 0 or u > 1:
            continue
        x, y = sp(u); k = i / n
        od.ellipse([x - 3 - 7 * k, y - 3 - 7 * k, x + 3 + 7 * k, y + 3 + 7 * k], fill=(255, 214, 140, int(150 * k * k)))
    if 0 < ts < 1:
        x, y = sp(ts)
        od.ellipse([x - 160, y - 160, x + 160, y + 160], fill=(255, 214, 140, 20))
        sat(od, x, y, 2.4)
    img = over(img, ov)
    ov, od = newov()
    od.polygon([(0, H)] + [(x, 930 + 36 * math.sin(x / 210 + .8) + 14 * math.sin(x / 60)) for x in range(0, 1100, 30)] + [(1100, H)], fill=(5, 7, 12, 255))
    img = over(img, ov)
    g = G(ImageDraw.Draw(img))
    k = E((t - .3) / 1.2)
    silhouette(g, 250, 960, 250 * k, math.sin(t * 1.1))
    silhouette(g, 370, 975, 215 * k, math.sin(t * 1.1 + 1.4))
    d = ImageDraw.Draw(img)
    a1 = E((t - 6.8) / .8)
    if a1 > 0:
        tx(d, (180, 130), "ESTADOS UNIDOS", 38, fc(t, 6.8, WH), 'la')
        tx(d, (W - 180, 130), "UNIÃO SOVIÉTICA", 38, fc(t, 7.2, WH), 'ra')
        x1 = 180 + 420 * 1.0; x2 = W - 180 - 440
        L = lerp(0, 1, E((t - 7.4) / 1.2))
        d.line([x1 + 20, 150, lerp(x1 + 20, 960 - 40, L), 150], fill=OR, width=3)
        d.line([x2 - 20, 150, lerp(x2 - 20, 960 + 40, L), 150], fill=OR, width=3)
        tx(d, (960, 150), "GUERRA FRIA", 30, fc(t, 8.2, OR), 'mm', 'm')
    return img


# ============================================================ 2  Sputnik
def h2(t):
    d_ = DURS[1]
    img = stars(bg('h2', [(0, BLACK), (.6, (10, 16, 40)), (1, (18, 30, 70))]), t, off=(t * 4, 0))
    img = earth(img, 1480, 1380, 700, t + 3, spin=26)
    ov, od = newov()
    orb = (420, 640, 2500, 1120)
    prog = E(t / 2.4)
    od.arc(orb, 180, 180 + 360 * prog, fill=(244, 214, 130, 170), width=4)
    img = over(img, ov)
    ang = t * .8 + 3.7
    ex = (orb[0] + orb[2]) / 2 + (orb[2] - orb[0]) / 2 * math.cos(ang)
    ey = (orb[1] + orb[3]) / 2 + (orb[3] - orb[1]) / 2 * math.sin(ang)
    g = G(ImageDraw.Draw(img))
    V.sputnik(g, ex, ey, 18 + 10 * (.5 + .5 * math.sin(ang)), t * 2)
    hx, hy = 1080, 400
    ov, od = newov()
    for i in range(6):
        ph = ((t * .8 - i * .3) % 1.8)
        rr = 60 + ph * 330
        od.ellipse([hx - rr, hy - rr, hx + rr, hy + rr], outline=(244, 214, 130, int(190 * (1 - ph / 1.8))), width=3)
    img = over(img, ov)
    g = G(ImageDraw.Draw(img))
    k = E((t - .5) / 1.0)
    V.sputnik(g, hx, hy + 20 * math.sin(t * .8), 78 * k, t * 1.4)
    d = ImageDraw.Draw(img)
    img = glowtext(img, (330, 210), "1957", int(230 * max(.01, E((t - .4) / .9))), OR, k=.55)
    d = ImageDraw.Draw(img)
    tx(d, (140, 340), "4 DE OUTUBRO  ·  BAIKONUR", 34, fc(t, 1.2, BEIGE), 'la', 'm')
    for i, (lab, sub, t0) in enumerate((("58 cm", "diâmetro", 2.0), ("83,6 kg", "massa", 2.8), ("4 antenas", "rádio 20 e 40 MHz", 3.6))):
        y0 = 520 + i * 120
        kk = E((t - t0) / .6)
        if kk > 0:
            d.line([140, y0 + 32, 140 + 70 * kk, y0 + 32], fill=OR, width=3)
            d.ellipse([134, y0 + 26, 146, y0 + 38], fill=OR)
            tx(d, (240, y0), lab, 48, mix(BLACK, WH, kk))
            tx(d, (240, y0 + 56), sub, 26, mix(BLACK, GRAY, kk), 'la', 'm')
    # barras de "bipe"
    for i in range(40):
        gate = 1.0 if ((t * 1.6 + i * .06) % 1.0) < .5 else 0.15
        hh = 14 + 70 * gate * (.6 + .4 * math.sin(t * 9 + i))
        al = E((t - 4.0) / 1.0)
        d.rectangle([140 + i * 14, 940 - hh, 140 + i * 14 + 8, 940], fill=mix(BLACK, YL, al))
    tx(d, (140, 970), "BIP · BIP · BIP", 24, fc(t, 4.2, GRAY), 'la', 'mono')
    return img


# ============================================================ 3  Gagarin
def h3(t):
    d_ = DURS[2]
    split = d_ * .56
    img = stars(bg('h3', [(0, BLACK), (.6, (8, 14, 36)), (1, (20, 36, 80))]), t, off=(-t * 10, 0))
    img = earth(img, 960 - 40 * clamp(t / d_), 1700, 1250, t * 1.2 + 9, spin=22)
    ov, od = newov()
    for i, off in enumerate((0, 50, 100)):
        od.arc([-400, 680 + off, 2320, 1900 + off], 205, 335, fill=(244, 214, 130, int(150 / (1 + i))), width=3 if i == 0 else 2)
    img = over(img, ov)
    ph = clamp(t / split)
    cx = lerp(1000, 1180, IO(ph)) + 8 * math.sin(t * 2); cy = 470 + 20 * math.sin(t * 1.4)
    ov, od = newov()
    for i in range(30):
        u = i / 30
        od.ellipse([cx - 300 - i * 18 - 10, cy - 10 - i * 2, cx - 280 - i * 18 + 10 + 10 * u, cy + 10 + i * 2], fill=(255, 190, 110, int(70 * (1 - u))))
    img = over(img, ov)
    g = G(ImageDraw.Draw(img))
    s = 270
    g.poly([(cx - s * .88, cy - s * .48), (cx - s * 2.1, cy - s * .32), (cx - s * 2.1, cy + s * .32), (cx - s * .88, cy + s * .48)], (80, 84, 98))
    for q in range(5):
        g.line([(cx - s * (1.05 + q * .2), cy - s * .44 + q * 8), (cx - s * (1.05 + q * .2), cy + s * .44 - q * 8)], (50, 54, 66), 3)
    g.line([(cx - s * 2.1, cy - 20), (cx - s * 2.4, cy - 90)], (200, 204, 214), 4)
    V.capsule_cut(g, cx, cy, s, t)
    d = ImageDraw.Draw(img)
    img = glowtext(img, (330, 190), "1961", int(210 * max(.01, E((t - .3) / .9))), OR, k=.55)
    d = ImageDraw.Draw(img)
    tx(d, (140, 320), "12 DE ABRIL  ·  VOSTOK 1", 34, fc(t, 1.0, BEIGE), 'la', 'm')
    tx(d, (140, 372), "108 MINUTOS EM ÓRBITA", 28, fc(t, 1.6, OR), 'la', 'm')
    for lab, x1, y1, x2, y2, t0 in (("Cosmonauta", 560, 840, cx - 80, cy + 170, 1.8), ("Escotilha", 1700, 800, cx - 190, cy - 30, 2.4)):
        kk = E((t - t0) / .5)
        if kk > 0:
            d.line([x1, y1, x1 + (x2 - x1) * kk, y1 + (y2 - y1) * kk], fill=BEIGE, width=2)
            tx(d, (x1, y1 + 10), lab, 30, mix(BLACK, BEIGE, kk), 'ra' if x1 > 960 else 'la', 'mono')
    if t > split:
        q = clamp((t - split) / (d_ * .3))
        Rr = lerp(60, 520, IO(q))
        px = lerp(cx - 186, 960, IO(q)); py = lerp(cy - 60, 540, IO(q))
        win = stars(Image.new('RGB', (W, H), (4, 6, 14)), t, off=(t * 8, 0))
        win = earth(win, 960, 1480 - 100 * q, 1000, t * 1.4, spin=30)
        wm = Image.new('L', (W, H), 0)
        ImageDraw.Draw(wm).ellipse([px - Rr, py - Rr, px + Rr, py + Rr], fill=255)
        wm = wm.filter(ImageFilter.GaussianBlur(2))
        img = Image.composite(win, img, wm)
        d = ImageDraw.Draw(img)
        d.ellipse([px - Rr, py - Rr, px + Rr, py + Rr], outline=(60, 64, 78), width=int(14 + 24 * q))
        d.ellipse([px - Rr - 8, py - Rr - 8, px + Rr + 8, py + Rr + 8], outline=(150, 154, 166), width=3)
        for i in range(14):
            an = i / 14 * 6.283
            rr = Rr + 10 + 12 * q
            d.ellipse([px + rr * math.cos(an) - 6, py + rr * math.sin(an) - 6, px + rr * math.cos(an) + 6, py + rr * math.sin(an) + 6], fill=(190, 194, 204))
    return img


# ============================================================ 4  Kennedy / a promessa
def h4(t):
    d_ = DURS[3]
    img = bg('h4', [(0, (5, 8, 22)), (.45, (16, 28, 64)), (.72, (88, 70, 96)), (.82, (206, 112, 56)), (.83, (14, 16, 24)), (1, (6, 8, 14))])
    img = stars(img, t, appear=1.0, depth=0.0)
    mz = 1.0 + .04 * clamp(t / d_)
    mx, my = 1450, 330
    ov, od = newov()
    for rr, al in ((420, 22), (330, 34), (270, 52)):
        od.ellipse([mx - rr, my - rr, mx + rr, my + rr], fill=(244, 214, 130, al))
    img = over(img, ov)
    img = moon(img, mx, my, 220 * mz)
    ov, od = newov()
    ring = 250 + 12 * math.sin(t * 2)
    od.ellipse([mx - ring, my - ring, mx + ring, my + ring], outline=(244, 214, 130, int(130 * E((t - 5) / 1.5))), width=3)
    img = over(img, ov)
    # Capitolio estilizado
    d = ImageDraw.Draw(img)
    d.rectangle([0, 780, 1100, 900], fill=(20, 22, 34))
    d.rectangle([180, 760, 960, 800], fill=(26, 28, 42))
    for i in range(14):
        d.rectangle([220 + i * 52, 800, 236 + i * 52, 880], fill=(32, 34, 50))
    d.pieslice([430, 520, 710, 800], 180, 360, fill=(24, 26, 40))
    d.rectangle([570 - 30, 480, 570 + 30, 540], fill=(24, 26, 40))
    d.pieslice([570 - 34, 440, 570 + 34, 520], 180, 360, fill=(24, 26, 40))
    d.line([570, 440, 570, 400], fill=(24, 26, 40), width=4)
    # tribuna e orador
    g = G(d)
    g.rect(1020, 880, 1180, 1080, (12, 14, 22))
    sway = math.sin(t * 1.2)
    silhouette(g, 1100, 880, 260, sway * .6, col=(8, 10, 16))
    gs = 1.0
    d.rectangle([1090, 760, 1094, 820], fill=(30, 32, 44))
    d.ellipse([1086, 752, 1098, 764], fill=(60, 62, 74))
    # plateia
    rnd = random.Random(4)
    for i in range(46):
        x = 40 + i * 42 + rnd.uniform(-10, 10)
        y = 1030 + rnd.uniform(0, 40) + 4 * math.sin(t * 1.5 + i)
        d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=(8, 10, 16))
        d.rectangle([x - 28, y + 14, x + 28, y + 70], fill=(8, 10, 16))
    # diagrama Terra - Lua
    ex, ey = 1210, 560
    img = earth(img, ex, ey, 46, t, base_r=100, spin=60)
    d = ImageDraw.Draw(img)
    u = E((t - 4.5) / 2.2)
    for i in range(int(36 * u)):
        a = i / 36
        x = lerp(ex + 50, mx - 230, a); y = lerp(ey - 20, my + 160, a) - 40 * math.sin(a * math.pi)
        d.ellipse([x - 3.5, y - 3.5, x + 3.5, y + 3.5], fill=YL)
    tx(d, (1210, 650), "384.400 km", 40, fc(t, 5.2, WH), 'mm')
    tx(d, (140, 130), "25 DE MAIO DE 1961", 52, fc(t, .6, WH), 'la')
    tx(d, (140, 202), "DISCURSO AO CONGRESSO DOS EUA", 28, fc(t, 1.2, BEIGE), 'la', 'm')
    tx(d, (140, 262), "ANTES DO FIM DA DÉCADA", 34, fc(t, 6.0, OR), 'la', 'm')
    return img


# ============================================================ 5  Saturno V (camera sobe)
def h5(t):
    d_ = DURS[4]
    p = clamp((t - .8) / (d_ - 2.4))
    k = 14.0
    gy = 2900
    cy = lerp(gy - 470, gy - 1170, IO(p))
    stops = [(gy - 3800, (5, 7, 18)), (gy - 2300, (12, 24, 58)), (gy - 800, (54, 58, 96)), (gy - 200, (186, 104, 66)), (gy - 20, (230, 130, 56)), (gy - 19, (20, 22, 30)), (gy + 500, (10, 12, 18))]
    img = to_img(V.vgrad_world(stops, cy))
    if cy < gy - 600:
        img = stars(img, t, appear=clamp((gy - 600 - cy) / 700) * .9, depth=0.0)
    mxs, mys = 1640, 300 + (cy - (gy - 1170)) * .35
    img = moon(img, mxs, mys, 130)
    ov, od = newov()
    for x in range(-40, W + 60, 40):
        pass
    img = over(img, ov)
    g = G(ImageDraw.Draw(img), Cam(960, cy))
    g.rect(0, gy, W, gy + 800, (20, 22, 30))
    g.rect(0, gy, W, gy + 8, (50, 54, 70))
    rx = 1150
    V.torre(g, rx + 9.1 * k + 40, gy, k, 120, t)
    V.saturn(g, rx, gy, k, t)
    g.rect(rx - 7 * k, gy - 3 * k, rx + 9 * k, gy, (70, 74, 88))
    for i in range(12):
        bx = 520 + i * 90 + 30 * math.sin(t * .6 + i)
        V.eng(g, bx, gy + 6 + (i % 3) * 7, 42, t * 5 + i)
    for i, m in enumerate((30, 55)):
        V.eng(g, rx + 130 + i * 30 + 20 * math.sin(t + i), gy - m * k, 34, t * 4 + i * 2)
    d = ImageDraw.Draw(img)
    def sy(m):
        return (gy - m * k - cy) + 540
    labs = [(108, "111 m", "de altura", 1.2, 'm'), (60, "2.900 t", "no lançamento", 3.0, 'm'), (14, "5 motores F-1", "primeiro estágio", 4.6, 'm')]
    for m, big, sub, t0, _ in labs:
        kk = E((t - t0) / .6)
        y = sy(m)
        if kk > 0 and -40 < y < H + 40:
            x2 = rx - 5 * k - 14
            x1 = lerp(x2, 640, kk)
            d.line([x1, y, x2, y], fill=OR, width=3)
            d.ellipse([x2 - 6, y - 6, x2 + 6, y + 6], fill=OR)
            tx(d, (x1 - 20, y - 6), big, 52, mix(BLACK, WH, kk), 'rd')
            tx(d, (x1 - 20, y + 8), sub, 26, mix(BLACK, BEIGE, kk), 'ra', 'm')
    q = E((t - (d_ - 5.4)) / 1.0)
    if q > 0:
        tx(d, (140, 920), "+400 MIL PESSOAS", 46, mix(BLACK, WH, q), 'la')
        tx(d, (140, 982), "NO PROGRAMA APOLLO", 28, mix(BLACK, OR, q), 'la', 'm')
    return img


# ============================================================ 6  Apollo 8 / Terra surge
def h6(t):
    d_ = DURS[5]; p = clamp(t / d_)
    img = stars(bg('h6', [(0, (0, 0, 3)), (1, (6, 8, 16))]), t, appear=1.0, depth=0.0)
    ex = 1280 + 40 * p
    ey = lerp(1060, 560, E(clamp((t - 1.5) / (d_ * .6))))
    ov, od = newov()
    od.ellipse([ex - 230, ey - 230, ex + 230, ey + 230], fill=(90, 160, 255, 26))
    img = over(img, ov)
    img = earth(img, ex, ey, 140 + 12 * p, t, base_r=140, spin=30)
    img = V.lunar_ground(img, -t * 4, t, 860)
    g = G(ImageDraw.Draw(img))
    u = clamp((t - .5) / (d_ - 1.5))
    sx = lerp(-260, 2200, u); sy_ = 330 + 40 * math.sin(u * 3)
    ov, od = newov()
    for i in range(50):
        a = i / 50
        od.ellipse([sx - 200 - a * 700 - 3, sy_ - 3, sx - 200 - a * 700 + 3, sy_ + 3], fill=(255, 220, 160, int(110 * (1 - a))))
    img = over(img, ov)
    g = G(ImageDraw.Draw(img))
    csm(g, sx, sy_, 1.05, 0.0, flame=0.0, t=t)
    d = ImageDraw.Draw(img)
    tx(d, (140, 120), "24 DE DEZEMBRO DE 1968", 52, fc(t, .5, WH), 'la')
    tx(d, (140, 192), "APOLLO 8 · O PRIMEIRO NASCER DA TERRA", 30, fc(t, 1.1, OR), 'la', 'm')
    tx(d, (140, 246), "Borman · Lovell · Anders  ·  10 voltas ao redor da Lua", 26, fc(t, 2.2, GRAY), 'la', 'm')
    return img


# ============================================================ 7  Lancamento
def h7(t):
    d_ = DURS[6]
    cut = d_ * .5
    if t < cut + .15:
        stops = [(0, (40, 70, 130)), (500, (210, 150, 100)), (760, (246, 190, 110)), (761, (60, 70, 60)), (1400, (30, 36, 34))]
        img = to_img(V.vgrad_world(stops, 540))
        ov, od = newov()
        for i in range(10):
            x = (i * 260 + t * 9) % (W + 400) - 200
            od.ellipse([x - 230, 200 + (i % 3) * 70, x + 230, 280 + (i % 3) * 70], fill=(255, 236, 210, 70))
        ov = ov.filter(ImageFilter.GaussianBlur(14))
        img = over(img, ov)
        gy = 860
        up = max(0, t - 2.0)
        rise = .5 * 50 * up ** 2
        cam = Cam(960, 540 - clamp(rise / 1300) * 200)
        g = G(ImageDraw.Draw(img), cam)
        g.rect(0, gy, W, 1400, (60, 70, 60))
        g.rect(0, gy, W, gy + 5, (96, 104, 90))
        k = 6.4
        V.torre(g, 980 + 80, gy, k, 120, t)
        g.rect(700, gy - 12, 1100, gy, (70, 74, 88))
        by = gy - rise
        fl = clamp((t - 1.0) / .8) * (1.0 if t > 2.0 else .55)
        V.saturn(g, 960, by, k, t, flame=fl)
        img = V.smoke(img, 960, gy + 8 - (cam.cy - 540) * -1, t - 1.0, spread=1.0 + rise / 800, seed=3)
        a2 = np.asarray(img).astype(np.float32)
        add_glow(a2, 960, (by - cam.cy) + 540 + 60, 600, (255, 150, 50), .55 * fl)
        img = to_img(a2)
        if t > 1.0:
            dx, dy = int(3 * math.sin(t * 61)), int(3 * math.cos(t * 53))
            img = img.transform((W, H), Image.AFFINE, (1, 0, dx, 0, 1, dy))
        d = ImageDraw.Draw(img)
        tx(d, (140, 120), "16 DE JULHO DE 1969", 52, fc(t, .5, WH), 'la')
        tx(d, (140, 192), "CABO KENNEDY · FLÓRIDA · 9h32", 28, fc(t, 1.0, BEIGE), 'la', 'm')
        tx(d, (140, 242), "APOLLO 11", 34, fc(t, 1.6, OR), 'la', 'm')
        return img
    tt = t - cut
    span = d_ - cut - .6
    alt = 62 * E(tt / (span * .8)) ** 1.3
    sp = 2.7 * E(tt / (span * .75))
    frac = clamp(alt / 62)
    stops = [(0, mix((60, 110, 190), (4, 6, 16), frac ** .8)), (1080, mix((170, 200, 240), (20, 34, 80), frac ** .7))]
    img = to_img(V.vgrad_world(stops, 540))
    if frac > .5:
        img = stars(img, t, appear=clamp((frac - .5) * 2.2), depth=0.0)
    ov, od = newov()
    rnd = random.Random(9)
    for n, spd, sc, al in ((10, 1000, 1.0, 140), (8, 1700, 1.5, 170), (6, 2600, 2.2, 190)):
        for i in range(n):
            x0 = rnd.uniform(-100, W + 100); ph = rnd.uniform(0, 2600)
            y = (ph + tt * spd * (1 - .6 * frac)) % 1600 - 250
            w_ = rnd.uniform(160, 320) * sc; h_ = w_ * .4
            a_ = int(al * (1 - frac * .8))
            od.ellipse([x0 - w_, y - h_, x0 + w_, y + h_], fill=(250, 246, 240, a_))
    ov = ov.filter(ImageFilter.GaussianBlur(3))
    img = over(img, ov)
    ov, od = newov()
    for i in range(44):
        x = rnd.uniform(0, W); y = (rnd.uniform(0, 1300) + tt * 3400) % 1500 - 200; L = rnd.uniform(120, 420)
        od.line([x, y, x, y + L], fill=(255, 255, 255, 70), width=2)
    img = over(img, ov)
    g = G(ImageDraw.Draw(img), Cam(960, 540))
    V.saturn(g, 960 + 3 * math.sin(tt * 20), 1010, 9.2, t, flame=1.0)
    a2 = np.asarray(img).astype(np.float32)
    add_glow(a2, 960, 1050, 520, (255, 170, 70), .5)
    img = to_img(a2)
    d = ImageDraw.Draw(img)
    d.line([160, 180, 160, 980], fill=(240, 240, 240), width=2)
    off = (tt * 260) % 60
    for i in range(-1, 16):
        y = 180 + i * 60 + off
        if 180 <= y <= 980:
            d.line([160, y, 200 if i % 5 == 0 else 182, y], fill=(240, 240, 240), width=2)
    my = 980 - 800 * frac
    d.polygon([(220, my), (250, my - 14), (250, my + 14)], fill=OR)
    tx(d, (270, my), f"{alt:0.0f} km", 52, WH, 'lm')
    tx(d, (270, my + 48), "ALTITUDE", 24, BEIGE, 'lm', 'mono')
    tx(d, (W - 140, 180), f"{sp:0.1f} km/s".replace('.', ','), 70, WH, 'ra')
    tx(d, (W - 140, 262), "VELOCIDADE", 24, BEIGE, 'ra', 'mono')
    tx(d, (W - 140, 304), "1º ESTÁGIO · S-IC", 24, OR, 'ra', 'mono')
    tx(d, (W - 140, 900), "Armstrong · Aldrin · Collins", 32, fc(t, cut + 1.2, WH), 'ra', 'm')
    return img


# ============================================================ 8  Viagem Terra -> Lua
def h8(t):
    d_ = DURS[7]; p = clamp((t - .6) / (d_ - 1.6))
    img = stars(bg('h8', [(0, BLACK), (1, (10, 14, 34))]), t, off=(-t * 14, 0))
    img = earth(img, 300, 720, 230, t, spin=24)
    img = moon(img, 1640, 360, 100)
    P0 = (470, 640); P1 = (1050, 190); P2 = (1560, 340)
    def bz(u):
        return ((1 - u) ** 2 * P0[0] + 2 * (1 - u) * u * P1[0] + u * u * P2[0], (1 - u) ** 2 * P0[1] + 2 * (1 - u) * u * P1[1] + u * u * P2[1])
    d = ImageDraw.Draw(img)
    for i in range(int(70 * clamp(E((t - .3) / 1.5)))):
        a = i / 70
        x, y = bz(a)
        if i % 2 == 0:
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(244, 214, 130))
    u = E(p)
    x, y = bz(u)
    x2, y2 = bz(min(1, u + .01))
    ang = math.atan2(y2 - y, x2 - x)
    ov, od = newov()
    od.ellipse([x - 90, y - 90, x + 90, y + 90], fill=(255, 214, 140, 24))
    img = over(img, ov)
    g = G(ImageDraw.Draw(img))
    csm(g, x, y, .9, ang)
    d = ImageDraw.Draw(img)
    day = 1 + int(u * 3.99)
    tx(d, (960, 880), "DIA", 28, fc(t, .8, BEIGE), 'rm', 'mono')
    tx(d, (990, 880), f"{day} / 4", 54, fc(t, .8, WH), 'lm')
    d.rectangle([560, 950, 1360, 958], fill=(40, 44, 60))
    d.rectangle([560, 950, 560 + 800 * u, 958], fill=OR)
    tx(d, (960, 140), "384.400 km", 64, fc(t, .5, WH), 'mm')
    tx(d, (960, 206), "ÓRBITA LUNAR EM 19 DE JULHO", 26, fc(t, 1.4, OR), 'mm', 'm')
    return img


# ============================================================ 9  Pouso
def h9(t):
    d_ = DURS[8]
    touch = d_ * .72
    img = stars(bg('h9', [(0, (0, 0, 4)), (1, (10, 12, 20))]), t, appear=1.0, depth=0.0)
    hz = 800
    img = earth(img, 1560, 250, 58, t, base_r=100, spin=40)
    img = V.lunar_ground(img, 0.0, t, hz)
    descend = IO(clamp(t / touch))
    sc = lerp(1.3, 1.9, descend)
    ground_y = 930
    y_base = lerp(120, ground_y, IO(clamp(t / touch)))
    x_ = 960 + 22 * math.sin(t * .8) * (1 - descend)
    thrust = 0.0
    if t < touch:
        thrust = 1.0 - .3 * clamp((t - touch * .6) / (touch * .4))
    elif t < touch + .8:
        thrust = clamp(1 - (t - touch) / .5)
    comp = 0.0
    if t >= touch:
        comp = math.exp(-(t - touch) * 4) * math.sin((t - touch) * 14) * .9 + .5 * math.exp(-(t - touch) * 5)
    ov, od = newov()
    od.ellipse([x_ - 150 * sc, ground_y - 8, x_ + 150 * sc, ground_y + 24], fill=(0, 0, 0, int(120 * descend)))
    img = over(img, ov)
    g = G(ImageDraw.Draw(img))
    V.lm(g, x_, y_base, sc, t, thrust=thrust, comp=comp)
    ov, od = newov()
    rnd = random.Random(8)
    if t > touch - 1.4:
        for i in range(160):
            ang = rnd.uniform(-.2, math.pi + .2); sp_ = rnd.uniform(200, 1100)
            u = clamp((t - (touch - 1.2 + rnd.uniform(0, .6))) / 3.0)
            if u <= 0:
                continue
            x = x_ + math.cos(ang) * sp_ * u * (1 if i % 2 else -1) * (1.2 if i % 3 else .6)
            y = ground_y + 10 - abs(math.sin(ang)) * 120 * u * (1 - u) * 3 + rnd.uniform(-6, 6)
            r = rnd.uniform(5, 16) * (1 + u * .8)
            od.ellipse([x - r, y - r * .6, x + r, y + r * .6], fill=(200, 196, 188, int(150 * (1 - u))))
    img = over(img, ov)
    d = ImageDraw.Draw(img)
    tx(d, (140, 120), "20 DE JULHO DE 1969", 52, fc(t, .8, WH), 'la')
    tx(d, (140, 192), "20h17 UTC · MAR DA TRANQUILIDADE", 28, fc(t, 1.4, YL), 'la', 'm')
    if t < touch + .2:
        alt = max(0, (ground_y - y_base) / 6.0)
        tx(d, (140, 940), f"ALT {alt:0.0f} m".replace('.', ','), 34, fc(t, 1.0, BEIGE), 'la', 'mono')
        if touch * .55 < t < touch:
            on = int(t * 3) % 2 == 0
            tx(d, (W - 140, 140), "CONTROLE MANUAL", 44, OR if on else mix(BLACK, OR, .35), 'ra')
            d.rectangle([W - 140 - 420, 190, W - 140, 194], fill=OR)
    return img


# ============================================================ 10 Primeiro passo
def h10(t):
    d_ = DURS[9]
    horizon = 1180
    A_end = d_ * .28; B_end = d_ * .52
    img = stars(bg('h10', [(0, (0, 0, 2)), (.6, (3, 4, 10)), (1, (8, 10, 18))]), t, depth=0.0)
    if t < A_end:
        cam = Cam(790, 1130, lerp(2.3, 2.1, t / A_end))
    elif t < B_end:
        u = IO((t - A_end) / 1.0)
        cam = Cam(lerp(790, 640, u), lerp(1130, 1280, u), lerp(2.1, 6.5, u))
    else:
        u = IO((t - B_end) / (d_ * .38))
        cam = Cam(lerp(640, 760, u), lerp(1280, 930, u), lerp(6.5, 1.0, u))
    z = cam.z
    ex, ey = 270, 420
    px, py = (ex - cam.cx) * z + W / 2, (ey - cam.cy) * z + H / 2
    if -300 < px < W + 300 and -300 < py < H + 300:
        img = earth(img, px, py, 78 * z, t, base_r=100, spin=30)
    hy = (horizon - cam.cy) * z + H / 2
    ov, od = newov()
    od.rectangle([0, max(0, hy), W, H], fill=(112, 112, 120, 255))
    img = over(img, ov)
    a = np.asarray(img).astype(np.float32)
    ys = np.arange(H)
    fa = np.clip((ys - hy) / max(1, (H - hy)), 0, 1)[:, None, None]
    a = np.where((ys > hy)[:, None, None], a * (1.0 - .45 * np.broadcast_to(fa, (H, W, 1))), a)
    img = to_img(a)
    g = G(ImageDraw.Draw(img), cam)
    rnd = random.Random(21)
    for i in range(30):
        x = rnd.uniform(-900, 2200); y = rnd.uniform(horizon + 30, horizon + 520); r = rnd.uniform(30, 120)
        g.ell(x - r, y - r * .22, x + r, y + r * .22, fill=(78, 78, 86))
        g.ell(x - r * .9, y - r * .16, x + r * .9, y + r * .2, fill=(120, 120, 128))
    lmx, lmy = 830, 1190
    gx = G(ImageDraw.Draw(img), cam)
    gx.poly([(lmx - 80, lmy + 4), (lmx + 80, lmy + 4), (lmx - 480, lmy + 60), (lmx - 640, lmy + 52)], (64, 64, 72))
    V.lm(gx, lmx, lmy, 1.0, t)
    gx.line([(lmx - 56, lmy - 118), (lmx - 150, lmy - 8)], (230, 230, 236), 7)
    gx.line([(lmx - 40, lmy - 118), (lmx - 134, lmy - 8)], (200, 200, 208), 7)
    for q in range(7):
        u2 = q / 6
        gx.line([(lmx - 52 - 90 * u2, lmy - 110 + 100 * u2), (lmx - 38 - 90 * u2, lmy - 110 + 100 * u2)], (150, 150, 160), 5)
    if t < A_end + .6:
        u2 = clamp(t / (A_end - .3))
        V.astronaut(gx, lmx - 76 - 96 * u2, lmy - 106 + 112 * u2, 120, ph=t * 2.2, arm=t * 2, face=-1, dark=.15)
    elif t < B_end:
        bx, by = lmx - 215, 1290
        T0 = A_end + .2
        tch = A_end + (B_end - A_end) * .45
        lift = (1 - E((t - T0) / 1.0)) * 150 + E((t - (tch + .5)) / .55) * 190
        if tch < t < tch + .9:
            ov, od = newov()
            r2 = random.Random(3)
            for q in range(34):
                u2 = clamp((t - tch - r2.uniform(0, .15)) / .9)
                an = r2.uniform(-.3, math.pi + .3)
                pxx = bx + math.cos(an) * 150 * u2 * r2.uniform(.5, 1.4); pyy = by + 14 - abs(math.sin(an)) * 90 * u2 * (1 - u2) * 3
                pp = gx.P(pxx, pyy)
                od.ellipse([pp[0] - 4, pp[1] - 4, pp[0] + 4, pp[1] + 4], fill=(180, 180, 188, int(200 * (1 - u2))))
            img = over(img, ov)
            gx = G(ImageDraw.Draw(img), cam)
        if t > tch:
            V.footprint(gx, bx, by + 10, 1.0)
        V.boot(gx, bx, by, 1.0, lift=lift)
    if t >= B_end:
        V.footprint(gx, lmx - 215, 1300, 1.0)
        u2 = clamp((t - B_end + .2) / (d_ * .3))
        ax = lerp(lmx - 215, 520, E(u2)); ay = lerp(1292, 1330, E(u2))
        for q in range(4):
            fx = lmx - 215 - q * 52
            if fx > ax:
                V.footprint(gx, fx, 1296 + q * 4, .35)
        V.astronaut(gx, ax, ay, 240, ph=t * 1.6 * (1 - E(u2) * .85), arm=t, face=-1, dark=.15)
        gx.poly([(ax - 18, ay + 2), (ax + 18, ay + 2), (ax + 520, ay + 70), (ax + 420, ay + 52)], (58, 58, 66))
    fx = 1010
    gx.line([(fx, 1250), (fx, 1130)], (220, 220, 226), 4)
    gx.rect(fx, 1130, fx + 90, 1176, (230, 230, 236))
    gx.rect(fx, 1130, fx + 36, 1152, (40, 60, 130))
    for q in range(4):
        gx.rect(fx + 36, 1130 + q * 12 + 2, fx + 90, 1130 + q * 12 + 8, (196, 60, 52))
    d = ImageDraw.Draw(img)
    if t > B_end + .5:
        kk = E((t - B_end - .5) / 1.0)
        tx(d, (140, 120), "Neil Armstrong", 60, mix(BLACK, WH, kk), 'la')
        tx(d, (140, 198), "21 DE JULHO DE 1969 · 02h56 UTC", 28, mix(BLACK, YL, kk), 'la', 'm')
        q2 = E((t - B_end - 3.0) / 1.2)
        if q2 > 0:
            tx(d, (W - 140, 900), "“Um pequeno passo para um homem,", 40, mix(BLACK, WH, q2), 'ra', 'm')
            tx(d, (W - 140, 954), "um salto gigantesco para a humanidade.”", 40, mix(BLACK, WH, q2), 'ra', 'm')
    return img


# ============================================================ 11 Caminhada lunar
def h11(t):
    d_ = DURS[10]
    p = clamp(t / d_)
    pan = lerp(0, -90, p)
    img = stars(bg('h11', [(0, (0, 0, 2)), (.7, (3, 4, 10)), (1, (8, 10, 18))]), t, depth=0.0)
    img = earth(img, 1010 + pan * .2, 230, 90, t, base_r=100, spin=30)
    img = V.lunar_ground(img, pan * .5, t, 640)
    g = G(ImageDraw.Draw(img), Cam(960 - pan, 540))
    gy = 760
    # LM a esquerda
    g.poly([(330 - 120, gy + 6), (330 + 100, gy + 6), (330 + 640, gy + 70), (330 + 480, gy + 56)], (64, 64, 72))
    V.lm(g, 330, gy, 1.25, t)
    # bandeira
    fx = 1180
    g.line([(fx, gy + 6), (fx, gy - 150)], (220, 220, 226), 5)
    g.rect(fx, gy - 150, fx + 120, gy - 92, (230, 230, 236))
    g.rect(fx, gy - 150, fx + 48, gy - 120, (40, 60, 130))
    for q in range(4):
        g.rect(fx + 48, gy - 150 + q * 14 + 3, fx + 120, gy - 150 + q * 14 + 10, (196, 60, 52))
    # experimentos
    g.rect(1480, gy - 22, 1540, gy + 8, (190, 190, 198), r=4)
    g.line([(1510, gy - 22), (1510, gy - 70)], (210, 210, 218), 4)
    g.circ(1510, gy - 74, 10, fill=(244, 214, 130))
    # astronautas
    u = (t * .06) % 1
    ax = lerp(560, 1080, E(clamp(t / (d_ * .85))))
    for q in range(8):
        fxx = ax - 60 - q * 70
        if fxx > 460:
            V.footprint(g, fxx, gy + 20 + (q % 2) * 4, .28)
    g.poly([(ax - 20, gy + 14), (ax + 20, gy + 14), (ax + 640, gy + 86), (ax + 540, gy + 70)], (58, 58, 66))
    V.astronaut(g, ax, gy + 14, 230, ph=t * 2.0 * (1 - .8 * E(clamp(t / (d_ * .85)))), arm=t * 1.5, face=1, dark=.1)
    bx2 = 700
    sw = math.sin(t * 1.6)
    g.poly([(bx2 - 20, gy + 50), (bx2 + 20, gy + 50), (bx2 + 560, gy + 120), (bx2 + 470, gy + 104)], (58, 58, 66))
    V.astronaut(g, bx2, gy + 50, 250, ph=0, arm=t * 2.4, face=1, dark=.1, visor=True)
    # ferramenta de coleta
    g.line([(bx2 + 40, gy - 60), (bx2 + 120, gy + 40)], (170, 170, 178), 5)
    g.rect(bx2 + 112, gy + 36, bx2 + 140, gy + 46, (140, 140, 148))
    d = ImageDraw.Draw(img)
    k1 = E((t - 1.2) / .8)
    tx(d, (W - 140, 130), "2h31", 96, mix(BLACK, WH, k1), 'ra')
    tx(d, (W - 140, 240), "NA SUPERFÍCIE", 28, mix(BLACK, BEIGE, k1), 'ra', 'm')
    k2 = E((t - 3.6) / .8)
    tx(d, (W - 140, 330), "21,5 kg", 72, mix(BLACK, YL, k2), 'ra')
    tx(d, (W - 140, 416), "DE ROCHAS LUNARES", 28, mix(BLACK, BEIGE, k2), 'ra', 'm')
    k3 = E((t - 6.0) / .8)
    tx(d, (140, 130), "MAR DA TRANQUILIDADE", 34, mix(BLACK, WH, k3), 'la', 'm')
    tx(d, (140, 184), "bandeira · sismômetro · refletor a laser", 26, mix(BLACK, GRAY, k3), 'la', 'm')
    return img


# ============================================================ 12 Retorno (amerissagem)
def h12(t):
    d_ = DURS[11]
    img = bg('h12', [(0, (30, 44, 96)), (.35, (140, 96, 120)), (.56, (246, 170, 100)), (.6, (60, 112, 130)), (1, (22, 52, 72))])
    ov, od = newov()
    sx, sy_ = 1500, 560
    od.ellipse([sx - 80, sy_ - 80, sx + 80, sy_ + 80], fill=(255, 226, 160, 255))
    for i in range(6):
        x = (i * 380 + t * 10) % (W + 500) - 250
        od.ellipse([x - 220, 150 + (i % 3) * 60, x + 220, 220 + (i % 3) * 60], fill=(255, 220, 190, 60))
    ov = ov.filter(ImageFilter.GaussianBlur(10))
    a2 = np.asarray(img).astype(np.float32)
    add_glow(a2, sx, sy_, 520, (255, 170, 90), .6)
    img = over(to_img(a2), ov)
    d = ImageDraw.Draw(img)
    # mar
    hz = 648
    for kx in range(10):
        y = hz + 20 + kx * 42
        pts = [(x, y + 5 * math.sin(x / 70 + t * 1.4 + kx)) for x in range(0, W + 20, 20)]
        d.line(pts, fill=(150, 200, 215), width=2)
    for i in range(18):
        x = (i * 113 + t * 18) % W; y = hz + 30 + (i * 53) % 380
        d.line([x, y, x + 40, y], fill=(255, 226, 170), width=2)
    # navio ao longe
    d.rectangle([420, hz - 18, 640, hz + 2], fill=(26, 34, 48))
    d.rectangle([520, hz - 40, 580, hz - 18], fill=(34, 42, 58))
    # capsula e paraquedas
    land = d_ * .62
    u = IO(clamp((t - .5) / (land - .5)))
    cx = lerp(900, 1020, u) + 24 * math.sin(t * 1.4) * (1 - u)
    cy = lerp(-120, 720, u)
    if t > land:
        cy = 720 + 6 * math.sin((t - land) * 2.2)
    g = G(d)
    if t < land + .4:
        al = 1 - E((t - land) / .4)
        for j, off in enumerate((-250, 0, 250)):
            top = cy - 640 + abs(off) * .15
            pxm = cx + off * (1 - .3 * u)
            col = (232, 106, 40) if j != 1 else (246, 244, 238)
            for q in range(6):
                a0 = math.pi + q * math.pi / 6; a1 = a0 + math.pi / 6
                pts = [(pxm, top + 70)] + [(pxm + 150 * math.cos(a0 + (a1 - a0) * s_), top + 70 + 130 * math.sin(a0 + (a1 - a0) * s_)) for s_ in (0, .5, 1)]
                g.poly(pts, col if q % 2 == 0 else (246, 244, 238))
            for q in range(-3, 4):
                g.line([(pxm + q * 50, top + 70), (cx + q * 6, cy - 50)], (40, 40, 48), 1)
    g.poly([(cx - 22, cy - 60), (cx + 22, cy - 60), (cx + 58, cy + 30), (cx - 58, cy + 30)], (176, 180, 190))
    g.poly([(cx - 58, cy + 30), (cx + 58, cy + 30), (cx + 50, cy + 46), (cx - 50, cy + 46)], (60, 62, 72))
    g.poly([(cx + 8, cy - 60), (cx + 22, cy - 60), (cx + 58, cy + 30), (cx + 20, cy + 30)], (140, 144, 156))
    if t > land:
        w = t - land
        ov, od = newov()
        for i in range(4):
            r = 40 + w * 120 + i * 40
            od.ellipse([cx - r, 740 - r * .16, cx + r, 740 + r * .16], outline=(255, 255, 255, int(160 * max(0, 1 - w / 3 - i * .1))), width=3)
        r2 = random.Random(2)
        for i in range(40):
            a = r2.uniform(0, math.pi); v = r2.uniform(60, 220)
            tt = clamp(w / 1.2)
            x = cx + math.cos(a) * v * tt * (1 if i % 2 else -1); y = 730 - math.sin(a) * v * tt * (1 - tt) * 4
            od.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 255, 255, int(200 * (1 - tt))))
        img = over(img, ov)
        d = ImageDraw.Draw(img)
    d = ImageDraw.Draw(img)
    tx(d, (140, 120), "24 DE JULHO DE 1969", 52, fc(t, .6, WH), 'la')
    tx(d, (140, 192), "COLUMBIA · OCEANO PACÍFICO", 28, fc(t, 1.2, YL), 'la', 'm')
    tx(d, (140, 246), "8 dias, 3 horas e 18 minutos de missão", 26, fc(t, 2.6, BEIGE), 'la', 'm')
    return img


# ============================================================ 13 Legado
def h13(t):
    d_ = DURS[12]; p = clamp(t / d_)
    img = stars(bg('h13', [(0, BLACK), (.6, (8, 12, 30)), (1, (16, 26, 60))]), t, off=(0, t * 3))
    z = lerp(1.3, .86, IO(p))
    cx, cy = 960, 520
    def mp(x, y):
        return ((x - cx) * z + cx, (y - cy) * z + cy)
    ex, ey = mp(760, 610)
    mx, my = mp(1560, 330)
    img = earth(img, ex, ey, 300 * z, t, spin=28)
    img = moon(img, mx, my, 110 * z)
    d = ImageDraw.Draw(img)
    kk = E((t - .6) / 1.4)
    for i in range(int(44 * kk)):
        a = i / 44
        x = lerp(ex + 300 * z * .8, mx - 110 * z, a); y = lerp(ey - 160 * z, my + 30 * z, a) - 80 * z * math.sin(a * math.pi)
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=YL)
    ov, od = newov()
    for i in range(4):
        rx = (440 + i * 100) * z; ry = (130 + i * 36) * z
        od.ellipse([ex - rx, ey - ry - 30 * z, ex + rx, ey + ry - 30 * z], outline=(244, 214, 130, 70), width=2)
    img = over(img, ov)
    d = ImageDraw.Draw(img)
    for i in range(4):
        rx = (440 + i * 100) * z; ry = (130 + i * 36) * z
        for j in range(2 + (i % 2)):
            a_ = t * (.7 - i * .12) + i * 1.7 + j * 3.14
            sx = ex + rx * math.cos(a_); sy_ = ey - 30 * z + ry * math.sin(a_)
            sz = (6 + 4 * (math.sin(a_) * .5 + .5)) * z
            if i == 2 and j == 0:
                d.rectangle([sx - 40 * z, sy_ - 4 * z, sx + 40 * z, sy_ + 4 * z], fill=(220, 224, 232))
                for sg in (-1, 1):
                    xa, xb = sorted((sx + sg * 46 * z, sx + sg * 90 * z))
                    d.rectangle([xa, sy_ - 14 * z, xb, sy_ + 14 * z], fill=(40, 70, 140), outline=(190, 205, 240))
            else:
                d.rectangle([sx - sz, sy_ - sz * .6, sx + sz, sy_ + sz * .6], fill=(230, 230, 236))
                d.rectangle([sx - sz * 3, sy_ - sz * .3, sx - sz * 1.1, sy_ + sz * .3], fill=(40, 70, 140))
                d.rectangle([sx + sz * 1.1, sy_ - sz * .3, sx + sz * 3, sy_ + sz * .3], fill=(40, 70, 140))
    ux = lerp(-160, 2100, E(clamp((t - 2.0) / 9)))
    uy = 200 + 30 * math.sin(t * .8)
    d.polygon([(ux - 60, uy), (ux + 40, uy - 8), (ux + 70, uy), (ux + 40, uy + 8)], fill=(240, 240, 244))
    d.polygon([(ux - 20, uy), (ux - 50, uy + 26), (ux - 2, uy + 4)], fill=(200, 204, 214))
    # contadores
    c1 = E((t - 2.5) / .8)
    if c1 > 0:
        tx(d, (140, 70), "6 MISSÕES", 52, mix(BLACK, WH, c1), 'la')
        tx(d, (140, 134), "POUSARAM NA LUA · 1969–1972", 24, mix(BLACK, BEIGE, c1), 'la', 'm')
    c2 = E((t - 5.5) / .8)
    if c2 > 0:
        tx(d, (140, 186), "12 PESSOAS", 52, mix(BLACK, YL, c2), 'la')
        tx(d, (140, 250), "CAMINHARAM EM SUA SUPERFÍCIE", 24, mix(BLACK, BEIGE, c2), 'la', 'm')
    # linha do tempo
    ov, od = newov()
    od.rounded_rectangle([90, 820, W - 90, 1010], radius=26, fill=(6, 10, 26, 205))
    img = over(img, ov)
    d = ImageDraw.Draw(img)
    ev = [(1957, "Sputnik 1"), (1961, "Gagarin"), (1969, "Apollo 11"), (1971, "Salyut 1"), (1981, "Ônibus espacial"), (1998, "ISS")]
    ty = 910
    x0, x1 = 180, W - 180
    tl = E((t - 3.0) / 2.5)
    d.line([x0, ty, x0 + (x1 - x0) * tl, ty], fill=(236, 236, 240), width=3)
    for i, (yr, lab) in enumerate(ev):
        xx = x0 + (x1 - x0) * (yr - 1957) / (1998 - 1957)
        t0 = 3.4 + i * .9
        kb = BACK((t - t0) / .5)
        if kb <= 0:
            continue
        r = 12 * kb
        colr = OR if yr == 1969 else YL
        d.ellipse([xx - r, ty - r, xx + r, ty + r], fill=colr)
        al = E((t - t0) / .5)
        up = (i % 2 == 0)
        ly = ty - 60 if up else ty + 60
        tx(d, (xx, ly), str(yr), 40, mix(BLACK, colr, al), 'mm')
        tx(d, (xx, ly + (-36 if up else 36)), lab, 24, mix(BLACK, BEIGE, al), 'mm', 'm')
    # cartao final
    e = E((t - (d_ - 3.2)) / 1.2)
    if e > 0:
        ov, od = newov()
        od.rectangle([0, 0, W, H], fill=(4, 6, 14, int(210 * e)))
        img = over(img, ov)
        img = glowtext(img, (960, 470), "A CORRIDA ESPACIAL", 110, WH, k=.4)
        d = ImageDraw.Draw(img)
        tx(d, (960, 580), "1957  —  1972", 40, mix(BLACK, OR, e), 'mm', 'm')
    return img


SCENES = [h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13]
