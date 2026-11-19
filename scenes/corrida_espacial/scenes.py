from common import *

DURS = [9.0, 8.2, 6.8, 7.8, 8.0, 10.0, 7.0, 10.2]
STARTS = [sum(DURS[:i]) for i in range(8)]
TOTAL = sum(DURS)


def vgrad_world(stops, cy, z=1.0):
    ys = (np.arange(H) - H / 2) / z + cy
    pos = [s[0] for s in stops]
    a = np.stack([np.interp(ys, pos, [s[1][c] for s in stops]) for c in range(3)], axis=1)
    return np.repeat(a[:, None, :], W, axis=1).astype(np.float32)


# ================================================================== CENA 1
def s1(t):
    p = clamp(t / 9.0)
    a = grad('s1', [(0, BLACK), (.5, (8, 12, 30)), (1, (16, 26, 60))])
    img = to_img(a)
    img = stars(img, t, off=(0, t * 6), appear=E(t / 5.0))
    # Terra: camera avancando
    R = lerp(720, 1020, IO(p))
    cy = lerp(1560, 1640, IO(p))
    img = earth(img, 560, cy, R, t, spin=30)
    d = ImageDraw.Draw(img)
    # satelite com rastro luminoso
    ov, od = newov()
    ts = clamp((t - 0.8) / 6.4)
    def spos(u):
        return (lerp(-200, 1280, u), lerp(700, 420, u) + 60 * math.sin(u * 3.0))
    n = 46
    for i in range(n):
        u = ts - (n - i) * 0.006
        if u <= 0 or u > 1:
            continue
        x, y = spos(u)
        k = i / n
        od.ellipse([x - 3 - 6 * k, y - 3 - 6 * k, x + 3 + 6 * k, y + 3 + 6 * k], fill=(255, 214, 140, int(150 * k * k)))
    if 0 < ts < 1:
        x, y = spos(ts)
        ang = t * 1.2
        sk = 2.4
        od.ellipse([x - 150, y - 150, x + 150, y + 150], fill=(255, 214, 140, 22))
        od.rectangle([x - 22 * sk, y - 12 * sk, x + 22 * sk, y + 12 * sk], fill=(224, 224, 232, 255))
        od.rectangle([x - 22 * sk, y - 12 * sk, x + 22 * sk, y - 5 * sk], fill=(206, 100, 40, 255))
        od.rectangle([x - 22 * sk, y + 6 * sk, x + 22 * sk, y + 12 * sk], fill=(170, 174, 186, 255))
        for sg in (-1, 1):
            xa, xb = sorted((x + sg * 28 * sk, x + sg * 90 * sk))
            od.rectangle([xa, y - 9 * sk, xb, y + 9 * sk], fill=(30, 60, 130, 255), outline=(190, 208, 244, 255), width=2)
            for q in range(1, 4):
                xx = x + sg * (28 + q * 15.5) * sk
                od.line([xx, y - 9 * sk, xx, y + 9 * sk], fill=(190, 208, 244, 230), width=2)
            od.line([xa, y, xb, y], fill=(190, 208, 244, 200), width=1)
        od.line([x, y - 12 * sk, x, y - 38 * sk], fill=(224, 224, 232, 255), width=4)
        od.ellipse([x - 8, y - 38 * sk - 8, x + 8, y - 38 * sk + 8], fill=(244, 214, 130, 255))
    img = over(img, ov)
    # primeiro plano: duas silhuetas observando
    ov, od = newov()
    ridge = [(0, H)] + [(x, 1590 + 40 * math.sin(x / 190 + .8) + 18 * math.sin(x / 63)) for x in range(0, W + 30, 30)] + [(W, H)]
    od.polygon(ridge, fill=(5, 7, 12, 255))
    img = over(img, ov)
    g = G(ImageDraw.Draw(img))
    sw = math.sin(t * 1.1)
    k = E((t - 0.2) / 1.2)
    silhouette(g, 250, 1625, 250 * k, sw)
    silhouette(g, 360, 1640, 215 * k, math.sin(t * 1.1 + 1.4))
    # linhas orbitais sutis
    ov, od = newov()
    for i in range(3):
        rr = R * (1.12 + i * .06)
        od.arc([560 - rr, cy - rr * .38, 560 + rr, cy + rr * .38 + 400], 200, 340, fill=(244, 214, 130, int(60 * E((t - 1) / 2))), width=2)
    img = over(img, ov)
    return img


# ================================================================== CENA 2
def sputnik(g, x, y, s, rot, front=1.0):
    g.circ(x, y, s * 1.08, fill=(244, 214, 130, ))
    g.circ(x, y, s, fill=(200, 204, 214))
    g.circ(x - s * .25, y - s * .3, s * .55, fill=(232, 234, 240))
    g.circ(x - s * .4, y - s * .45, s * .18, fill=(255, 255, 255))
    # faixas
    g.line([(x - s, y), (x + s, y)], (150, 154, 166), 2)
    # 4 antenas
    for i, ang in enumerate((0.2, 0.55, math.pi - 0.2, math.pi - 0.55)):
        a = ang + math.sin(rot) * .06
        L = s * (3.6 if i < 2 else 3.2)
        g.line([(x + s * .8 * math.cos(a) * (1 if i < 2 else 1), y + s * .3 * math.sin(a)), (x + L * math.cos(a) * (1 if i < 2 else 1), y + L * .55 * math.sin(a) * -1 + s * .3)], (220, 224, 232), max(2, int(s * .05)))
    g.circ(x + s * .55, y + s * .6, s * .06, fill=(206, 100, 40))


def s2(t):
    p = clamp(t / 8.2)
    a = grad('s2', [(0, BLACK), (.55, (10, 16, 40)), (1, (18, 30, 70))])
    img = to_img(a)
    img = stars(img, t, off=(t * 4, 0), appear=1.0)
    R = 760
    cx, cy = 540, 1600
    img = earth(img, cx, cy + 60 - 30 * IO(p), R, t + 3, spin=30)
    ov, od = newov()
    # orbita (elipse) animada
    orb = (-120, 1060, 1200, 1500)
    prog = E(t / 2.2)
    od.arc(orb, 180, 180 + 360 * prog, fill=(244, 214, 130, 170), width=4)
    # pontos tracejados
    for i in range(48):
        ang = math.radians(i * 7.5 + t * 20)
        ex = (orb[0] + orb[2]) / 2 + (orb[2] - orb[0]) / 2 * math.cos(ang)
        ey = (orb[1] + orb[3]) / 2 + (orb[3] - orb[1]) / 2 * math.sin(ang)
        if i % 2 == 0 and prog > .98:
            od.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(244, 214, 130, 120))
    img = over(img, ov)
    # posicao do Sputnik na orbita
    ang = t * 0.95 + 3.6
    ex = (orb[0] + orb[2]) / 2 + (orb[2] - orb[0]) / 2 * math.cos(ang)
    ey = (orb[1] + orb[3]) / 2 + (orb[3] - orb[1]) / 2 * math.sin(ang)
    fr = 0.5 + 0.5 * math.sin(ang)
    s_ = 26 + 24 * fr
    # sinais de radio
    ov, od = newov()
    for i in range(5):
        ph = ((t * 0.9 - i * 0.28) % 1.4)
        rr = 20 + ph * 260
        al = int(200 * (1 - ph / 1.4)) if t > 1.0 else 0
        od.ellipse([ex - rr, ey - rr, ex + rr, ey + rr], outline=(244, 214, 130, al), width=3)
    img = over(img, ov)
    d = ImageDraw.Draw(img)
    g = G(d)
    sputnik(g, ex, ey, s_, t * 2)
    # data 1957 destacada
    k = BACK((t - 0.4) / 0.9)
    img = glowtext(img, (540, 330), "1957", int(250 * max(.01, k)), OR, k=0.6)
    d = ImageDraw.Draw(img)
    d.text((540, 480), "4 DE OUTUBRO  ·  BAIKONUR", font=font(34, 'm'), fill=mix(BLACK, BEIGE, E((t - 1.2) / .8)), anchor='mm')
    # infografico: chamadas
    items = [("58 cm", "diâmetro", 110, 590, 1.8), ("83,6 kg", "massa", 110, 700, 2.4), ("4 antenas", "rádio 20 e 40 MHz", 110, 810, 3.0)]
    for lab, sub, x0, y0, t0 in items:
        kk = E((t - t0) / .6)
        if kk <= 0:
            continue
        d.line([x0, y0 + 30, x0 + 6 + 90 * kk, y0 + 30], fill=OR, width=3)
        d.ellipse([x0 - 6, y0 + 24, x0 + 6, y0 + 36], fill=OR)
        c = mix(BLACK, WH, kk)
        d.text((x0 + 120, y0 + 6), lab, font=font(44, 'b'), fill=c)
        d.text((x0 + 120, y0 + 56), sub, font=font(26, 'm'), fill=mix(BLACK, GRAY, kk))
    return img


# ================================================================== CENA 3
def capsule_cut(g, x, y, s, t):
    # casco
    g.circ(x, y, s, fill=(70, 74, 88))
    g.circ(x, y, s * .93, fill=(214, 200, 172))
    g.circ(x, y, s * .93, outline=(120, 110, 96), w=3)
    # paineis de instrumentos (piscando)
    for i in range(5):
        on = (int(t * 3 + i * 1.7) % 3) != 0
        g.circ(x + s * (.45 + i * .0), y - s * (.45 - i * .2), s * .035, fill=OR if on else (110, 100, 90))
    g.rect(x + s * .3, y - s * .55, x + s * .78, y + s * .1, (60, 64, 78), r=6)
    # assento
    g.poly([(x - s * .5, y - s * .1), (x - s * .15, y - s * .1), (x - s * .1, y + s * .55), (x - s * .6, y + s * .6)], (120, 94, 70))
    # cosmonauta de traje laranja
    br = math.sin(t * 2) * s * .01
    g.poly([(x - s * .5, y - s * .55 + br), (x - s * .15, y - s * .55 + br), (x - s * .15, y + s * .3), (x - s * .5, y + s * .3)], OR)
    g.poly([(x - s * .5, y + s * .3), (x - s * .15, y + s * .3), (x + s * .1, y + s * .5), (x + s * .05, y + s * .62), (x - s * .5, y + s * .5)], (190, 86, 34))
    g.circ(x - s * .32, y - s * .72 + br, s * .17, fill=(240, 240, 244))
    g.circ(x - s * .27, y - s * .72 + br, s * .1, fill=(70, 100, 150))
    g.poly([(x - s * .2, y - s * .5), (x + s * .1, y - s * .35), (x + s * .12, y - s * .3), (x - s * .2, y - s * .4)], (200, 78, 30))
    # escotilha
    g.circ(x - s * .62, y - s * .2, s * .17, fill=(30, 50, 100))
    g.circ(x - s * .62, y - s * .2, s * .17, outline=(70, 74, 88), w=5)
    g.circ(x - s * .66, y - s * .26, s * .04, fill=(180, 210, 255))


def s3(t):
    p = clamp(t / 6.8)
    a = grad('s3', [(0, BLACK), (.6, (8, 14, 36)), (1, (20, 36, 80))])
    img = to_img(a)
    img = stars(img, t, off=(-t * 10, 0))
    # Terra grande ao fundo
    img = earth(img, 540 - 40 * p, 1650 + 40 * (1 - p), 1150, t * 1.2 + 9, spin=22)
    d = ImageDraw.Draw(img)
    # linhas de trajetoria
    ov, od = newov()
    for i, off in enumerate((0, 60, 120)):
        od.arc([-300, 760 + off, 1380, 1900 + off], 205, 335, fill=(244, 214, 130, int(150 / (1 + i))), width=3 if i == 0 else 2)
    img = over(img, ov)
    ph = clamp(t / 3.6)
    # Fase A: capsula atravessa; camera acompanha (capsula quase centralizada)
    cx = lerp(430, 640, IO(ph)) + 10 * math.sin(t * 2)
    cy = 820 + 24 * math.sin(t * 1.4)
    ov, od = newov()
    for i in range(30):
        u = i / 30
        od.ellipse([cx - 260 - i * 18 - 10, cy - 10 - i * 2, cx - 240 - i * 18 + 10 + 10 * u, cy + 10 + i * 2], fill=(255, 190, 110, int(70 * (1 - u))))
    img = over(img, ov)
    g = G(ImageDraw.Draw(img))
    # modulo de servico (cone/cilindro) atras
    g.poly([(cx - 220, cy - 120), (cx - 520, cy - 80), (cx - 520, cy + 80), (cx - 220, cy + 120)], (80, 84, 98))
    for q in range(5):
        g.line([(cx - 260 - q * 50, cy - 110 + q * 8), (cx - 260 - q * 50, cy + 110 - q * 8)], (50, 54, 66), 3)
    g.line([(cx - 520, cy - 20), (cx - 600, cy - 70)], (200, 204, 214), 4)
    g.circ(cx - 600, cy - 70, 8, fill=YL)
    capsule_cut(g, cx, cy, 250, t)
    d = ImageDraw.Draw(img)
    k = BACK((t - .3) / .8)
    img = glowtext(img, (540, 310), "1961", int(230 * max(.01, k)), OR, k=0.55)
    d = ImageDraw.Draw(img)
    d.text((540, 450), "VOSTOK 1  ·  108 MINUTOS EM ÓRBITA", font=font(30, 'm'), fill=mix(BLACK, BEIGE, E((t - 1.0) / .8)), anchor='mm')
    # etiquetas em corte
    for lab, x1, y1, x2, y2, t0 in (("Cosmonauta", 330, 1090, cx - 80, cy + 170, 1.3), ("Escotilha", 1000, 1000, cx - 150, cy - 40, 1.8)):
        kk = E((t - t0) / .5)
        if kk > 0:
            d.line([x1, y1, x1 + (x2 - x1) * kk, y1 + (y2 - y1) * kk], fill=BEIGE, width=2)
            d.text((x1 - 8, y1 + 14), lab, font=font(32, 'mono'), fill=mix(BLACK, BEIGE, kk), anchor='ra' if x1 > 540 else 'la')
    # Fase B: a camera se aproxima da escotilha e revela a curvatura da Terra
    if t > 3.2:
        q = clamp((t - 3.2) / 3.0)
        R = lerp(60, 520, IO(q))
        px, py = cx - 155, cy - 50
        px = lerp(px, 540, IO(q)); py = lerp(py, 900, IO(q))
        # vista da janela: curvatura
        win = Image.new('RGB', (W, H), (4, 6, 14))
        win = stars(win, t, off=(t * 8, 0))
        win = earth(win, 540, 1700 - 80 * q, 1000, t * 1.4, spin=30)
        wd = ImageDraw.Draw(win)
        wm = Image.new('L', (W, H), 0)
        ImageDraw.Draw(wm).ellipse([px - R, py - R, px + R, py + R], fill=255)
        wm = wm.filter(ImageFilter.GaussianBlur(2))
        img = Image.composite(win, img, wm)
        d = ImageDraw.Draw(img)
        d.ellipse([px - R, py - R, px + R, py + R], outline=(60, 64, 78), width=int(14 + 20 * q))
        d.ellipse([px - R - 8, py - R - 8, px + R + 8, py + R + 8], outline=(150, 154, 166), width=3)
        for i in range(12):
            an = i / 12 * 6.283
            rr = R + 10 + 10 * q
            d.ellipse([px + rr * math.cos(an) - 5, py + rr * math.sin(an) - 5, px + rr * math.cos(an) + 5, py + rr * math.sin(an) + 5], fill=(190, 194, 204))
    return img


# ================================================================== Saturno V
def saturn(g, x, by, k, t=0, flame=0.0):
    """x = centro, by = base (pes), k = px por metro"""
    def R(m0, m1, w, col):
        g.rect(x - w * k / 2, by - m1 * k, x + w * k / 2, by - m0 * k, col)
    # bocais
    for i in range(5):
        bx = x + (i - 2) * 1.9 * k
        g.poly([(bx - .6 * k, by - 5 * k), (bx + .6 * k, by - 5 * k), (bx + 1.1 * k, by), (bx - 1.1 * k, by)], (46, 46, 54))
    # aletas
    for sg in (-1, 1):
        g.poly([(x + sg * 5 * k, by - 6 * k), (x + sg * 9.4 * k, by - 3 * k), (x + sg * 9.4 * k, by - 3 * k + .0), (x + sg * 5 * k, by - 22 * k)], (30, 32, 40))
    WHC, S1, S2 = (240, 240, 244), (212, 214, 222), (176, 180, 192)
    R(5, 42, 10, WHC)
    g.rect(x + 2.2 * k, by - 42 * k, x + 3.4 * k, by - 5 * k, S1)
    g.rect(x + 3.4 * k, by - 42 * k, x + 5 * k, by - 5 * k, S2)
    for m0, m1 in ((5, 9), (24, 30), (38, 42)):
        g.rect(x - 5 * k, by - m1 * k, x + 5 * k, by - m0 * k, (22, 22, 28))
    R(42, 45, 10, (22, 22, 28))
    R(45, 67, 10, WHC)
    g.rect(x + 2.2 * k, by - 67 * k, x + 3.4 * k, by - 45 * k, S1)
    g.rect(x + 3.4 * k, by - 67 * k, x + 5 * k, by - 45 * k, S2)
    g.rect(x - 5 * k, by - 50 * k, x + 5 * k, by - 45 * k, (22, 22, 28))
    g.poly([(x - 5 * k, by - 67 * k), (x + 5 * k, by - 67 * k), (x + 3.4 * k, by - 70 * k), (x - 3.4 * k, by - 70 * k)], WHC)
    R(70, 85, 6.6, WHC)
    g.rect(x + 1.6 * k, by - 85 * k, x + 3.3 * k, by - 70 * k, S2)
    R(85, 88, 6.6, (22, 22, 28))
    g.poly([(x - 3.3 * k, by - 88 * k), (x + 3.3 * k, by - 88 * k), (x + 1.9 * k, by - 98 * k), (x - 1.9 * k, by - 98 * k)], WHC)
    g.poly([(x + .6 * k, by - 88 * k), (x + 3.3 * k, by - 88 * k), (x + 1.9 * k, by - 98 * k), (x + .6 * k, by - 98 * k)], S1)
    g.rect(x - .25 * k, by - 111 * k, x + .25 * k, by - 98 * k, (206, 100, 40))
    g.poly([(x - 1.0 * k, by - 98 * k), (x + 1.0 * k, by - 98 * k), (x + .25 * k, by - 103 * k), (x - .25 * k, by - 103 * k)], OR)
    g.poly([(x - .25 * k, by - 111 * k), (x + .25 * k, by - 111 * k), (x, by - 114 * k)], (230, 230, 232))
    g.circ(x, by - 62 * k, .0, fill=None)
    # bandeira
    g.rect(x - 4.4 * k, by - 18 * k, x - 1.2 * k, by - 15 * k, (30, 50, 120))
    # chama
    if flame > 0:
        L = flame * k * 28
        fl = 1 + .08 * math.sin(t * 40)
        g.poly([(x - 8 * k, by), (x + 8 * k, by), (x + 3 * k, by + L * .6 * fl), (x, by + L * fl), (x - 3 * k, by + L * .6 * fl)], (206, 100, 40))
        g.poly([(x - 5.5 * k, by), (x + 5.5 * k, by), (x + 1.5 * k, by + L * .5 * fl), (x, by + L * .75 * fl), (x - 1.5 * k, by + L * .5 * fl)], (244, 190, 90))
        g.poly([(x - 3 * k, by), (x + 3 * k, by), (x, by + L * .35 * fl)], (255, 244, 214))


def torre(g, x, by, k, h=120, t=0):
    top = by - h * k
    g.rect(x - 2.4 * k, top, x + 2.4 * k, by, None) if False else None
    for sg in (-1, 1):
        g.line([(x + sg * 2.4 * k, by), (x + sg * 2.4 * k, top)], (70, 76, 96), max(3, int(.5 * k)))
    n = int(h / 6)
    for i in range(n):
        y0 = by - i * 6 * k
        y1 = y0 - 6 * k
        g.line([(x - 2.4 * k, y0), (x + 2.4 * k, y1)], (56, 62, 80), max(2, int(.25 * k)))
        g.line([(x + 2.4 * k, y0), (x - 2.4 * k, y1)], (56, 62, 80), max(2, int(.25 * k)))
        g.line([(x - 2.4 * k, y0), (x + 2.4 * k, y0)], (70, 76, 96), max(2, int(.3 * k)))
    # bracos
    for m in (30, 55, 80, 96):
        g.rect(x + 2.4 * k, by - (m + .8) * k, x + 8.8 * k, by - (m - .8) * k, (96, 102, 122))
    on = int(t * 2) % 2 == 0
    g.circ(x, top - .8 * k, .8 * k, fill=(230, 60, 50) if on else (110, 40, 40))


def eng(g, x, y, s, ph, vest=OR):
    sw = math.sin(ph)
    g.rect(x - .12 * s, y - .5 * s, x + .12 * s, y - .02 * s, (40, 44, 58))
    g.rect(x - .16 * s, y - .98 * s, x + .16 * s, y - .5 * s, vest, r=int(.04 * s))
    g.circ(x, y - 1.1 * s, .12 * s, fill=(214, 168, 132))
    g.ell(x - .15 * s, y - 1.26 * s, x + .15 * s, y - 1.08 * s, fill=(246, 246, 240))
    g.line([(x - .1 * s, y - .02 * s), (x - .1 * s + sw * .12 * s, y)], (20, 20, 24), max(2, int(.1 * s)))


# ================================================================== CENA 4
def s4(t):
    p = clamp((t - 0.7) / 5.9)
    cy = lerp(2400, 900, IO(p))
    a = vgrad_world([(0, (5, 7, 18)), (1300, (12, 24, 58)), (2300, (54, 58, 96)), (2760, (186, 104, 66)), (2900, (230, 130, 56)), (2901, (20, 22, 30)), (3300, (10, 12, 18))], cy)
    img = to_img(a)
    # estrelas no alto
    if cy < 2000:
        img = stars(img, t, off=(0, 0), appear=clamp((2300 - cy) / 1800) * 0.9)
    # lua distante
    mx, my = 840, 330
    mz = Cam(540, cy * .95 + 40)
    mpx = (mx - mz.cx) + W / 2; mpy = (my - mz.cy) + H / 2
    img = moon(img, mpx, mpy, 120)
    ov, od = newov()
    for rr in (150, 200):
        od.ellipse([mpx - rr, mpy - rr, mpx + rr, mpy + rr], outline=(244, 214, 130, 40), width=2)
    img = over(img, ov)
    ov, od = newov()
    cb = Cam(540, cy * .86 + 380)
    hills = [(0, H * 3)] + [(x, 2850 + 50 * math.sin(x / 160) + 22 * math.sin(x / 47)) for x in range(0, W + 40, 40)] + [(W, H * 3)]
    pts = [((x - cb.cx) + W / 2, (y - cb.cy) + H / 2) for x, y in hills]
    od.polygon(pts, fill=(34, 36, 56, 255))
    img = over(img, ov)
    g = G(ImageDraw.Draw(img), Cam(540, cy))
    gy = 2900
    g.rect(0, gy, W, 3600, (20, 22, 30))
    g.rect(0, gy, W, gy + 10, (50, 54, 70))
    k = 22
    torre(g, 740, gy, k, 120, t)
    saturn(g, 540, gy, k, t)
    # plataforma de lancamento
    g.rect(300, gy - 3 * k, 800, gy, (70, 74, 88))
    g.rect(250, gy - 1.4 * k, 850, gy - 0, (50, 54, 66))
    # engenheiros
    rnd = random.Random(2)
    for i in range(9):
        bx = 120 + i * 100 + 40 * math.sin(t * .6 + i)
        by = gy + 6 + (i % 3) * 8
        eng(g, bx, by, 58, t * 5 + i)
    for i, ly in enumerate((gy - 30 * k, gy - 55 * k)):
        eng(g, 840 + i * 40 + 30 * math.sin(t + i), ly, 40, t * 4 + i * 2)
    eng(g, 690, gy - 80 * k, 38, t * 3)
    d = ImageDraw.Draw(img)
    # rotulos tecnicos
    labs = [(111, "111 m", 0), (85, "Módulo lunar + comando", 1), (42, "1º estágio · 5 motores F-1", 2)]
    # diagrama Terra-Lua
    q = E((t - 5.2) / 1.2)
    if q > 0:
        ov, od = newov()
        od.rounded_rectangle([60, 1040, W - 60, 1560], radius=28, fill=(10, 16, 36, int(200 * q)), outline=(244, 214, 130, int(160 * q)), width=2)
        img = over(img, ov)
        img = earth(img, 230, 1300, 100, t, base_r=100, spin=50) if q > 0.5 else img
        img = moon(img, 850, 1300, 28, base_r=40) if q > .5 else img
        d = ImageDraw.Draw(img)
        x2 = lerp(330, 820, E((t - 5.5) / 1.1))
        for xx in range(330, int(x2), 28):
            d.line([xx, 1300, xx + 14, 1300], fill=YL, width=3)
        d.text((540, 1250), "384.400 km", font=font(40, 'b'), fill=mix(BLACK, WH, q), anchor='mm')
        d.text((540, 1360), "ATÉ O FIM DA DÉCADA", font=font(26, 'm'), fill=mix(BLACK, OR, q), anchor='mm')
        d.text((90, 1070), "Fig. 1 · Rota Terra → Lua", font=font(22, 'mono'), fill=mix(BLACK, GRAY, q))
        d.text((540, 1440), "1962 — 1969", font=font(30, 'm'), fill=mix(BLACK, BEIGE, q), anchor='mm')
    return img


# ================================================================== CENA 5
def smoke(img, cx, cy, t, n=24, spread=1.0, seed=1):
    ov, od = newov()
    rnd = random.Random(seed)
    for i in range(n):
        ph = rnd.uniform(0, 1)
        life = clamp(t * 0.45 - ph * 0.5)
        if life <= 0:
            continue
        sd = rnd.choice((-1, 1))
        x = cx + sd * (60 + life * 520 * spread) * rnd.uniform(.5, 1.1)
        y = cy - life * 60 * rnd.uniform(.4, 1.2) - rnd.uniform(0, 30)
        r = 40 + life * 150 * rnd.uniform(.7, 1.3)
        od.ellipse([x - r, y - r * .8, x + r, y + r * .8], fill=(226, 214, 196, int(200 * (1 - life) ** .8)))
    ov = ov.filter(ImageFilter.GaussianBlur(6))
    return over(img, ov)


def s5(t):
    cut = 3.9
    if t < cut + 0.15:
        a = vgrad_world([(0, (40, 70, 130)), (1100, (210, 150, 100)), (1500, (246, 190, 110)), (1501, (60, 70, 60)), (2200, (30, 36, 34))], 700)
        img = to_img(a)
        ov, od = newov()
        for i in range(8):
            x = (i * 190 + t * 8) % (W + 300) - 150
            od.ellipse([x - 190, 400 + (i % 3) * 80, x + 190, 480 + (i % 3) * 80], fill=(255, 236, 210, 70))
        ov = ov.filter(ImageFilter.GaussianBlur(14))
        img = over(img, ov)
        gy = 1500
        up = max(0, t - 1.2)
        rise = 0.5 * 60 * up ** 2 * (1 if up < 2.6 else 1)
        cam = Cam(540, 960 + clamp(rise / 1400) * -240)
        g = G(ImageDraw.Draw(img), cam)
        g.rect(0, gy, W, 2300, (60, 70, 60))
        g.rect(0, gy, W, gy + 6, (96, 104, 90))
        k = 8.2
        torre(g, 700, gy, k, 120, t)
        g.rect(380, gy - 16, 760, gy, (70, 74, 88))
        by = gy - rise
        fl = clamp((t - 0.5) / 0.8) * (1.0 if t > 1.2 else .55)
        if t > .3:
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        saturn(g, 540, by, k, t, flame=fl)
        img = smoke(img, 540 - (cam.cx - 540) * 0, gy + 10 - (cam.cy - 960) * -1 * -1, t, spread=1.0 + rise / 800, seed=3)
        a2 = np.asarray(img).astype(np.float32)
        if t > .5:
            add_glow(a2, 540, (by - cam.cy) + 960 + 80, 700, (255, 150, 50), .55 * fl)
        img = to_img(a2)
        # tremor
        if t > 0.5:
            dx, dy = int(4 * math.sin(t * 61)), int(4 * math.cos(t * 53))
            img = img.transform((W, H), Image.AFFINE, (1, 0, dx, 0, 1, dy))
        # data
        d = ImageDraw.Draw(img)
        d.text((540, 190), "16 DE JULHO DE 1969", font=font(44, 'b'), fill=mix(BLACK, WH, E((t - .4) / .8)), anchor='mm')
        d.text((540, 250), "CABO KENNEDY · FLÓRIDA · 9h32", font=font(26, 'm'), fill=mix(BLACK, BEIGE, E((t - .8) / .8)), anchor='mm')
        return img
    # ---- close do foguete atravessando as nuvens
    tt = t - cut
    alt = 62 * E(tt / 4.0) ** 1.3
    sp = 2.7 * E(tt / 3.8)
    frac = clamp(alt / 62)
    a = vgrad_world([(0, mix((60, 110, 190), (4, 6, 16), frac ** .8)), (1920, mix((170, 200, 240), (20, 34, 80), frac ** .7))], 960)
    img = to_img(a)
    if frac > .5:
        img = stars(img, t, off=(0, 0), appear=clamp((frac - .5) * 2.2))
    ov, od = newov()
    rnd = random.Random(9)
    for layer, (n, spd, sc, al) in enumerate(((10, 900, 1.0, 140), (8, 1500, 1.5, 170), (6, 2400, 2.2, 190))):
        for i in range(n):
            x0 = rnd.uniform(-100, W + 100)
            ph = rnd.uniform(0, 2400)
            y = (ph + tt * spd * (1 - .6 * frac)) % 2600 - 300
            w_ = rnd.uniform(160, 320) * sc
            h_ = w_ * .4
            od.ellipse([x0 - w_, y - h_, x0 + w_, y + h_], fill=(250, 246, 240, int(al * (1 - frac * .8))))
            od.ellipse([x0 - w_ * .6 - 40, y - h_ * 1.2, x0 + w_ * .5, y + h_ * .3], fill=(255, 255, 255, int(al * (1 - frac * .8))))
    ov = ov.filter(ImageFilter.GaussianBlur(3))
    img = over(img, ov)
    # linhas de velocidade
    ov, od = newov()
    for i in range(36):
        x = rnd.uniform(0, W)
        y = (rnd.uniform(0, 2000) + tt * 3200) % 2200 - 200
        L = rnd.uniform(120, 420)
        od.line([x, y, x, y + L], fill=(255, 255, 255, 70), width=2)
    img = over(img, ov)
    g = G(ImageDraw.Draw(img), Cam(540, 960))
    k = 15.5
    flame = 1.0
    wob = 6 * math.sin(tt * 20)
    saturn(g, 540 + wob * .3, 1500, k, t, flame=flame)
    a2 = np.asarray(img).astype(np.float32)
    add_glow(a2, 540, 1560, 620, (255, 170, 70), .5)
    img = to_img(a2)
    # regua de altitude
    d = ImageDraw.Draw(img)
    d.line([90, 300, 90, 1500], fill=(240, 240, 240), width=2)
    off = (tt * 260) % 60
    for i in range(-1, 22):
        y = 300 + i * 60 + off
        if 300 <= y <= 1500:
            d.line([90, y, 130 if i % 5 == 0 else 112, y], fill=(240, 240, 240), width=2)
    my = 1500 - 1200 * frac
    d.polygon([(150, my), (180, my - 14), (180, my + 14)], fill=OR)
    d.text((200, my), f"{alt:0.0f} km", font=font(44, 'b'), fill=WH, anchor='lm')
    d.text((200, my + 44), "ALTITUDE", font=font(22, 'mono'), fill=BEIGE, anchor='lm')
    d.text((W - 80, 330), f"{sp:0.1f} km/s".replace('.', ','), font=font(60, 'b'), fill=WH, anchor='ra')
    d.text((W - 80, 400), "VELOCIDADE", font=font(22, 'mono'), fill=BEIGE, anchor='ra')
    d.text((W - 80, 440), "1º ESTÁGIO · S-IC", font=font(22, 'mono'), fill=OR, anchor='ra')
    return img


# ================================================================== CENA 6
def lunar_ground(img, cy_shift, t, horizon=1320):
    d = ImageDraw.Draw(img)
    # colinas distantes (parallax lento)
    ov, od = newov()
    for li, (col, amp, base, par) in enumerate(((((66, 66, 72, 255)), 26, horizon - 10, .15), ((92, 92, 98, 255), 20, horizon + 10, .35))):
        pts = [(0, H)] + [(x, base + amp * math.sin((x + cy_shift * par * 4) / (130 - li * 30)) + amp * .5 * math.sin((x + cy_shift * par * 4) / 41)) for x in range(0, W + 30, 30)] + [(W, H)]
        od.polygon(pts, fill=col)
    img = over(img, ov)
    a = np.asarray(img).astype(np.float32)
    ys = np.arange(H)
    m = (ys > horizon + 20)[:, None]
    f = np.clip((ys - horizon) / (H - horizon), 0, 1)[:, None]
    ground = np.stack([lerp(120, 84, f[:, 0]), lerp(120, 84, f[:, 0]), lerp(126, 92, f[:, 0])], axis=1)[:, None, :]
    a[m[:, 0]] = np.broadcast_to(ground[m[:, 0]], (int(m.sum()), W, 3))
    img = to_img(a)
    ov, od = newov()
    rnd = random.Random(3)
    for i in range(34):
        fy = rnd.random() ** 1.7
        y = horizon + 40 + fy * (H - horizon - 40) + cy_shift * (0.2 + fy * 2.4) % 1
        sc = .15 + fy * 1.7
        x = rnd.uniform(-100, W + 100)
        rx, ry = 90 * sc, 22 * sc
        od.ellipse([x - rx, y - ry, x + rx, y + ry], fill=(70, 70, 78, 190))
        od.ellipse([x - rx * .92, y - ry * .8, x + rx * .88, y + ry * .86], fill=(110, 110, 118, 220))
        od.arc([x - rx, y - ry, x + rx, y + ry], 200, 340, fill=(190, 190, 198, 190), width=max(1, int(3 * sc)))
    img = over(img, ov)
    return img


def lm(g, x, y, s, t, thrust=0.0, comp=0.0):
    """modulo lunar. y = base das pernas (chao). s = escala"""
    legy = y - 20 * s + comp * 6 * s
    for sg in (-1, 1):
        g.line([(x + sg * 38 * s, y - 100 * s), (x + sg * 100 * s, legy - 4 * s)], (200, 200, 208), max(2, int(5 * s)))
        g.line([(x + sg * 38 * s, y - 70 * s), (x + sg * 70 * s, legy - 4 * s)], (160, 160, 170), max(2, int(3 * s)))
        g.ell(x + sg * 100 * s - 24 * s, legy - 6 * s, x + sg * 100 * s + 24 * s, legy + 6 * s, fill=(230, 224, 200))
    # estagio de descida (dourado)
    g.poly([(x - 56 * s, y - 130 * s), (x + 56 * s, y - 130 * s), (x + 70 * s, y - 80 * s), (x + 50 * s, y - 56 * s), (x - 50 * s, y - 56 * s), (x - 70 * s, y - 80 * s)], (214, 164, 70))
    g.poly([(x - 20 * s, y - 130 * s), (x + 56 * s, y - 130 * s), (x + 70 * s, y - 80 * s), (x + 30 * s, y - 80 * s)], (240, 200, 110))
    for q in range(3):
        g.line([(x - 60 * s + q * 4 * s, y - 120 * s + q * 24 * s), (x + 60 * s - q * 4 * s, y - 120 * s + q * 24 * s)], (160, 118, 40), max(1, int(2 * s)))
    # estagio de subida (cinza com janelas)
    g.poly([(x - 44 * s, y - 130 * s), (x + 44 * s, y - 130 * s), (x + 50 * s, y - 188 * s), (x + 24 * s, y - 214 * s), (x - 24 * s, y - 214 * s), (x - 50 * s, y - 188 * s)], (212, 212, 220))
    g.poly([(x + 4 * s, y - 130 * s), (x + 44 * s, y - 130 * s), (x + 50 * s, y - 188 * s), (x + 24 * s, y - 214 * s), (x + 4 * s, y - 214 * s)], (176, 176, 188))
    g.poly([(x - 30 * s, y - 180 * s), (x - 10 * s, y - 180 * s), (x - 14 * s, y - 160 * s), (x - 32 * s, y - 164 * s)], (40, 44, 60))
    g.poly([(x + 10 * s, y - 180 * s), (x + 30 * s, y - 180 * s), (x + 32 * s, y - 164 * s), (x + 14 * s, y - 160 * s)], (40, 44, 60))
    g.line([(x, y - 214 * s), (x, y - 250 * s)], (220, 220, 230), max(2, int(3 * s)))
    g.circ(x, y - 252 * s, 6 * s, fill=(244, 214, 130))
    g.line([(x - 70 * s, y - 100 * s), (x - 110 * s, y - 112 * s)], (200, 200, 210), max(2, int(3 * s)))
    if thrust > 0:
        L = thrust * 140 * s * (1 + .12 * math.sin(t * 50))
        g.poly([(x - 14 * s, y - 56 * s), (x + 14 * s, y - 56 * s), (x + 4 * s, y - 56 * s + L), (x - 4 * s, y - 56 * s + L)], (244, 190, 90))
        g.poly([(x - 8 * s, y - 56 * s), (x + 8 * s, y - 56 * s), (x, y - 56 * s + L * .6)], (255, 244, 214))


def s6(t):
    p = clamp(t / 10.0)
    img = to_img(grad('s6', [(0, (0, 0, 4)), (.65, (4, 6, 12)), (1, (10, 12, 20))]))
    img = stars(img, t, off=(0, 0), appear=1.0, depth=0.0)
    horizon = 1320
    # Terra pequena e distante
    img = earth(img, 820, 640 + 10 * math.sin(t * .3), 62, t, base_r=100, spin=40) if False else earth(img, 820, 640, 62, t, base_r=100, spin=40)
    touch = 6.4
    descend = E(clamp(t / touch))  # 0..1
    shift = 0 if t < touch else 0
    img = lunar_ground(img, -descend * 0 + 0.0, t, horizon)
    ly = lerp(300, 1280 + 0, IO(clamp(t / touch)) ** 1.0)
    cz = 1.0 + 0.0
    g = G(ImageDraw.Draw(img), Cam(540, 960, 1.0))
    sc = lerp(1.6, 2.2, descend)
    thrust = 0.0
    if t < touch:
        thrust = 1.0 - 0.3 * clamp((t - 4) / 2.4)
    elif t < touch + .8:
        thrust = clamp(1 - (t - touch) / .5)
    comp = 0.0
    if t >= touch:
        comp = math.exp(-(t - touch) * 4) * math.sin((t - touch) * 14) * 0.9 + 0.5 * math.exp(-(t - touch) * 5)
    ground_y = 1290 + 40
    y_base = lerp(500, ground_y, IO(clamp(t / touch)) )
    x_ = 540 + 24 * math.sin(t * .8) * (1 - descend)
    # sombra
    ov, od = newov()
    sh = 1 - descend
    od.ellipse([x_ - 150 * sc * .9, ground_y - 8, x_ + 150 * sc * .9, ground_y + 26], fill=(0, 0, 0, int(120 * descend)))
    img = over(img, ov)
    g = G(ImageDraw.Draw(img))
    lm(g, x_, y_base, sc, t, thrust=thrust, comp=comp)
    # poeira
    ov, od = newov()
    rnd = random.Random(8)
    if t > touch - 1.4:
        for i in range(140):
            ang = rnd.uniform(-.2, math.pi + .2)
            sp_ = rnd.uniform(150, 900)
            u = clamp((t - (touch - 1.2 + rnd.uniform(0, .6))) / 3.0)
            if u <= 0:
                continue
            x = x_ + math.cos(ang) * sp_ * u * (1 if i % 2 else -1) * (1.2 if i % 3 else .6)
            y = ground_y + 10 - abs(math.sin(ang)) * 120 * u * (1 - u) * 3 + rnd.uniform(-6, 6)
            r = rnd.uniform(5, 16) * (1 + u * .8)
            od.ellipse([x - r, y - r * .6, x + r, y + r * .6], fill=(200, 196, 188, int(150 * (1 - u))))
    img = over(img, ov)
    d = ImageDraw.Draw(img)
    d.text((540, 190), "20 DE JULHO DE 1969", font=font(46, 'b'), fill=mix(BLACK, WH, E((t - 3.6) / .8)), anchor='mm')
    d.text((540, 250), "MAR DA TRANQUILIDADE", font=font(26, 'm'), fill=mix(BLACK, YL, E((t - 4.2) / .8)), anchor='mm')
    # leitura de altitude
    if t < touch + .2:
        alt = max(0, (ground_y - y_base) / 14)
        d.text((80, 1500), f"ALT {alt:0.0f} m".replace('.', ','), font=font(30, 'mono'), fill=mix(BLACK, BEIGE, E(t / 1.0)))
    return img


# ================================================================== CENA 7
def boot(g, x, y, s, lift=0.0):
    y = y - lift
    # cano e bota (vista lateral, ponta para a esquerda)
    g.poly([(x - 70 * s, y - 18 * s), (x - 68 * s, y - 36 * s), (x - 44 * s, y - 56 * s), (x - 12 * s, y - 70 * s), (x - 6 * s, y - 170 * s), (x + 56 * s, y - 170 * s), (x + 60 * s, y - 62 * s), (x + 74 * s, y - 18 * s)], (234, 234, 240))
    g.poly([(x + 18 * s, y - 170 * s), (x + 56 * s, y - 170 * s), (x + 60 * s, y - 62 * s), (x + 74 * s, y - 18 * s), (x + 22 * s, y - 18 * s), (x + 18 * s, y - 70 * s)], (204, 206, 216))
    for q in range(5):
        g.line([(x - 6 * s, y - (86 + q * 17) * s), (x + 57 * s, y - (86 + q * 17) * s)], (176, 178, 190), max(1, int(2.2 * s)))
    g.line([(x - 40 * s, y - 52 * s), (x - 8 * s, y - 66 * s)], (176, 178, 190), max(1, int(2.5 * s)))
    g.rect(x - 8 * s, y - 70 * s, x + 58 * s, y - 62 * s, (206, 100, 40))
    # sola grossa com sulcos
    g.rect(x - 74 * s, y - 20 * s, x + 78 * s, y, (64, 66, 76), r=int(5 * s))
    for q in range(-7, 8):
        g.rect(x + q * 10 * s - 3 * s, y - 2 * s, x + q * 10 * s + 3 * s, y + 4 * s, (40, 40, 48))
    # poeira lunar na bota
    rnd = random.Random(5)
    for i in range(18):
        px = x + rnd.uniform(-70, 74) * s; py = y - rnd.uniform(0, 34) * s
        g.circ(px, py, rnd.uniform(1.5, 3.5) * s, fill=(140, 140, 148))


def footprint(g, x, y, s):
    """pegada em perspectiva: toe a esquerda, com sulcos"""
    g.poly([(x - 80 * s, y + 6 * s), (x - 60 * s, y - 6 * s), (x + 60 * s, y - 6 * s), (x + 82 * s, y + 6 * s), (x + 62 * s, y + 20 * s), (x - 62 * s, y + 20 * s)], (52, 52, 60))
    g.line([(x - 80 * s, y + 6 * s), (x - 60 * s, y - 6 * s), (x + 60 * s, y - 6 * s), (x + 82 * s, y + 6 * s)], (170, 170, 178), max(1, int(2.5 * s)))
    g.line([(x - 62 * s, y + 20 * s), (x + 62 * s, y + 20 * s)], (30, 30, 36), max(1, int(2 * s)))
    for q in range(-6, 7):
        if abs(q) <= 1:
            continue
        g.line([(x + q * 10 * s, y - 3 * s), (x + q * 10 * s, y + 17 * s)], (112, 112, 120), max(1, int(2.5 * s)))
    # borda elevada ao redor
    g.line([(x - 84 * s, y + 4 * s), (x - 64 * s, y + 22 * s), (x + 64 * s, y + 22 * s), (x + 86 * s, y + 4 * s)], (140, 140, 148), max(1, int(2 * s)))


def s7(t):
    horizon = 1180
    img = to_img(grad('s7', [(0, (0, 0, 2)), (.6, (3, 4, 10)), (1, (8, 10, 18))]))
    img = stars(img, t, off=(0, 0), depth=0.0)
    # fases de camera
    # A: 0-2.6 escada ; B: 2.6-4.6 pegada ; C: 4.6-7.0 afastar
    A_end, B_end = 2.6, 4.6
    if t < A_end:
        cam = Cam(790, 1130, lerp(2.3, 2.1, t / A_end))
    elif t < B_end:
        u = IO((t - A_end) / 0.9)
        cam = Cam(lerp(790, 640, u), lerp(1130, 1280, u), lerp(2.1, 6.5, u))
    else:
        u = IO((t - B_end) / 2.4)
        cam = Cam(lerp(640, 600, u), lerp(1280, 1000, u), lerp(6.5, 1.0, u))
    # Terra no ceu (fixa no mundo)
    ex, ey = 270, 420
    ez = cam.z
    px, py = (ex - cam.cx) * ez + W / 2, (ey - cam.cy) * ez + H / 2
    if -200 < px < W + 200 and -200 < py < H + 200:
        img = earth(img, px, py, 78 * ez, t, base_r=100, spin=30)
    # solo (varia com camera)
    zz = cam.z
    hy = (horizon - cam.cy) * zz + H / 2
    ov, od = newov()
    od.rectangle([0, max(0, hy), W, H], fill=(112, 112, 120, 255))
    # gradiente de profundidade no solo
    img = over(img, ov)
    a = np.asarray(img).astype(np.float32)
    ys = np.arange(H)
    fa = np.clip((ys - hy) / max(1, (H - hy)), 0, 1)[:, None, None]
    fa = np.broadcast_to(fa, (H, W, 1))
    mask = (ys > hy)[:, None, None]
    a = np.where(mask, a * (1.0 - 0.45 * fa) , a)
    img = to_img(a)
    g = G(ImageDraw.Draw(img), cam)
    # crateras do mundo
    rnd = random.Random(21)
    for i in range(22):
        x = rnd.uniform(-300, 1500); y = rnd.uniform(horizon + 30, horizon + 500)
        r = rnd.uniform(30, 120)
        g.ell(x - r, y - r * .22, x + r, y + r * .22, fill=(78, 78, 86))
        g.ell(x - r * .9, y - r * .16, x + r * .9, y + r * .2, fill=(120, 120, 128))
    # modulo lunar + escada
    lmx = 830; lmy = 1190
    s_lm = 1.0
    # sombras longas
    ov, od = newov()
    sh = [(0, 0)]
    img = over(img, ov)
    gx = G(ImageDraw.Draw(img), cam)
    # sombra do LM
    gx.poly([(lmx - 80, lmy + 4), (lmx + 80, lmy + 4), (lmx - 480, lmy + 60), (lmx - 640, lmy + 52)], (64, 64, 72))
    lm(gx, lmx, lmy, 1.0, t)
    # escada
    ladx0, ladx1 = lmx - 62, lmx - 130
    gx.line([(lmx - 56, lmy - 118), (lmx - 150, lmy - 8)], (230, 230, 236), 7)
    gx.line([(lmx - 40, lmy - 118), (lmx - 134, lmy - 8)], (200, 200, 208), 7)
    for q in range(7):
        u = q / 6
        gx.line([(lmx - 52 - 90 * u, lmy - 110 + 100 * u), (lmx - 38 - 90 * u, lmy - 110 + 100 * u)], (150, 150, 160), 5)
    # astronauta
    if t < A_end + .6:
        u = clamp(t / 2.2)
        ax = lmx - 52 - 96 * u - 24
        ay = lmy - 110 + 112 * u + 4
        astronaut(gx, ax, ay + 130 * 0.0, 120, ph=t * 2.2, arm=t * 2, face=-1, dark=0.15)
    elif t < B_end:
        bx = lmx - 215
        by = 1290
        lift = (1 - E((t - A_end - 0.2) / 1.0)) * 150 + E((t - 4.05) / .55) * 190
        if t > 3.55 and t < 4.4:
            ov, od = newov()
            r2 = random.Random(3)
            for q in range(34):
                u = clamp((t - 3.55 - r2.uniform(0, .15)) / .9)
                ang = r2.uniform(-.3, math.pi + .3)
                px = bx + math.cos(ang) * 150 * u * r2.uniform(.5, 1.4)
                py = by + 14 - abs(math.sin(ang)) * 90 * u * (1 - u) * 3
                od.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(180, 180, 188, int(200 * (1 - u))))
            img = over(img, ov)
            gx = G(ImageDraw.Draw(img), cam)
        if t > 3.55:
            footprint(gx, bx, by + 10, 1.0)
        boot(gx, bx, by, 1.0, lift=lift)
    # pegada permanente (apos B)
    if t >= B_end:
        footprint(gx, lmx - 215, 1300, 1.0)
        # a bota permanece apenas ate sair
    if t < B_end and t >= A_end + 1.5:
        pass
    # fase C: astronauta em pe e trilha de pegadas
    if t >= B_end - .2:
        u = clamp((t - B_end + .2) / 2.6)
        ax = lerp(lmx - 215, 520, E(u))
        ay = lerp(1292, 1330, E(u))
        for q in range(4):
            fx = lmx - 215 - q * 52 * 1.0
            if fx > ax:
                footprint(gx, fx, 1296 + q * 4, .35)
        ov, od = newov()
        gx.poly([(ax - 40, ay), (ax + 40, ay), (ax + 560, ay + 30), (ax + 440, ay + 24)], (60, 60, 68)) if False else None
        astronaut(gx, ax, ay, 240 if u < 1 else 240, ph=t * 1.6 * (1 - E(u) * .85), arm=t, face=-1, dark=0.15)
        # sombra longa
        gx.poly([(ax - 18, ay + 2), (ax + 18, ay + 2), (ax + 520, ay + 70), (ax + 420, ay + 52)], (58, 58, 66))
    # bandeira
    fx = 1000
    gx.line([(fx, 1250), (fx, 1130)], (220, 220, 226), 4)
    gx.rect(fx, 1130, fx + 90, 1176, (230, 230, 236))
    gx.rect(fx, 1130, fx + 36, 1152, (40, 60, 130))
    for q in range(4):
        gx.rect(fx + 36, 1130 + q * 12 + 2, fx + 90, 1130 + q * 12 + 8, (196, 60, 52))
    d = ImageDraw.Draw(img)
    if t > B_end + 0.4:
        kk = E((t - B_end - .4) / 1.0)
        d.text((540, 220), "Neil Armstrong", font=font(54, 'b'), fill=mix(BLACK, WH, kk), anchor='mm')
        d.text((540, 286), "21 DE JULHO DE 1969 · 02h56 UTC", font=font(26, 'm'), fill=mix(BLACK, YL, kk), anchor='mm')
    return img


# ================================================================== CENA 8
def s8(t):
    p = clamp(t / 10.2)
    a = grad('s8', [(0, BLACK), (.6, (8, 12, 30)), (1, (16, 26, 60))])
    img = to_img(a)
    z = lerp(1.35, 0.78, IO(p))
    cx, cy = 540, 760
    img = stars(img, t, off=(0, t * 3), appear=1.0)
    ex, ey = 320, 820
    px, py = (ex - cx) * z + cx, (ey - cy) * z + cy
    mx, my = 820, 430
    qx, qy = (mx - cx) * z + cx, (my - cy) * z + cy
    img = earth(img, px, py, 330 * z, t, spin=28)
    img = moon(img, qx, qy, 120 * z)
    # link Terra-Lua
    d = ImageDraw.Draw(img)
    kk = E((t - 0.6) / 1.4)
    for i in range(int(40 * kk)):
        u = i / 40
        x = lerp(px + 380 * z * .55, qx - 120 * z, u)
        y = lerp(py - 280 * z * .6, qy + 40 * z, u) - 60 * z * math.sin(u * math.pi)
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=YL)
    # satelites orbitando
    ov, od = newov()
    for i in range(4):
        rx = (470 + i * 90) * z; ry = (160 + i * 40) * z
        od.ellipse([px - rx, py - ry - 40 * z, px + rx, py + ry - 40 * z], outline=(244, 214, 130, 70), width=2)
    img = over(img, ov)
    d = ImageDraw.Draw(img)
    g = G(d)
    for i in range(4):
        rx = (470 + i * 90) * z; ry = (160 + i * 40) * z
        for j in range(2 + (i % 2)):
            ang = t * (0.7 - i * .12) + i * 1.7 + j * 3.14
            sx = px + rx * math.cos(ang); sy = py - 40 * z + ry * math.sin(ang)
            sz = (7 + 4 * (math.sin(ang) * .5 + .5)) * z
            if i == 2 and j == 0:
                # ISS estilizada
                g2 = G(d)
                d.rectangle([sx - 40 * z, sy - 4 * z, sx + 40 * z, sy + 4 * z], fill=(220, 224, 232))
                for sg in (-1, 1):
                    d.rectangle([min(sx + sg * 46 * z, sx + sg * 90 * z), sy - 14 * z, max(sx + sg * 46 * z, sx + sg * 90 * z), sy + 14 * z], fill=(40, 70, 140), outline=(190, 205, 240))
            else:
                d.rectangle([sx - sz, sy - sz * .6, sx + sz, sy + sz * .6], fill=(230, 230, 236))
                d.rectangle([sx - sz * 3, sy - sz * .3, sx - sz * 1.1, sy + sz * .3], fill=(40, 70, 140))
                d.rectangle([sx + sz * 1.1, sy - sz * .3, sx + sz * 3, sy + sz * .3], fill=(40, 70, 140))
    # nave pequena (onibus espacial) cruzando
    sx = lerp(-120, 1200, E(clamp((t - 2) / 7)))
    sy = 420 + 40 * math.sin(t * .8)
    d.polygon([(sx - 60, sy), (sx + 40, sy - 8), (sx + 70, sy), (sx + 40, sy + 8)], fill=(240, 240, 244))
    d.polygon([(sx - 20, sy), (sx - 50, sy + 26), (sx - 2, sy + 4)], fill=(200, 204, 214))
    d.polygon([(sx - 60, sy - 2), (sx - 76, sy - 16), (sx - 60, sy - 12)], fill=(60, 64, 78))
    ov, od = newov()
    od.rounded_rectangle([40, 1300, W - 40, 1590], radius=26, fill=(6, 10, 26, 205))
    img = over(img, ov)
    d = ImageDraw.Draw(img)
    # linha do tempo
    ev = [(1957, "Sputnik 1", 0), (1961, "Gagarin", 1), (1969, "Apollo 11", 2), (1971, "Salyut 1", 3), (1981, "Ônibus espacial", 4), (1998, "ISS", 5)]
    ty = 1450
    x0, x1 = 90, 990
    tl = E((t - 1.4) / 2.0)
    d.line([x0, ty, x0 + (x1 - x0) * tl, ty], fill=(236, 236, 240), width=3)
    for i, (yr, lab, k) in enumerate(ev):
        xx = x0 + (x1 - x0) * (yr - 1957) / (1998 - 1957)
        t0 = 2.0 + i * 0.9
        kk = BACK((t - t0) / .5)
        if kk <= 0:
            continue
        r = 12 * kk
        colr = OR if yr == 1969 else YL
        d.ellipse([xx - r, ty - r, xx + r, ty + r], fill=colr)
        up = (i % 2 == 0)
        ly = ty - 120 if up else ty + 60
        d.line([xx, ty + (-r if up else r), xx, ly + (80 if up else 0)], fill=(150, 156, 168), width=2)
        al = E((t - t0) / .5)
        c1 = mix(BLACK, WH, al)
        d.text((xx, ly + (0 if up else 18)), str(yr), font=font(46, 'b'), fill=mix(BLACK, colr, al), anchor='mm')
        d.text((xx, ly + (44 if up else 62)), lab, font=font(28, 'm'), fill=mix(BLACK, BEIGE, al), anchor='mm')
    if t > 7.8:
        kk = E((t - 7.8) / 1.2)
        d.text((540, 300), "A CORRIDA ESPACIAL", font=font(52, 'b'), fill=mix(BLACK, WH, kk), anchor='mm')
        d.text((540, 366), "1957 — 1969", font=font(30, 'm'), fill=mix(BLACK, OR, kk), anchor='mm')
    return img


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8]
