import os, sys, json, subprocess, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO_DIR = os.environ.get('VIDEO_DIR', os.path.join(ROOT, 'scenes', 'corrida_espacial'))
OUT_DIR = os.environ.get('OUT_DIR', os.path.join(ROOT, 'out'))
TTS_DIR = os.path.join(OUT_DIR, 'tts')
sys.path.insert(0, VIDEO_DIR)
import scenes as SC
PARAMS = json.load(open(os.path.join(VIDEO_DIR, 'params.json')))

SR = 44100
TOTAL = SC.TOTAL
N = int((TOTAL + 2.0) * SR)
ST = SC.STARTS
NOFF = PARAMS['narr_offsets']
rng = np.random.default_rng(11)


def mid(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'low', fs=SR, output='sos'), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'high', fs=SR, output='sos'), x)


def bp(x, f1, f2):
    return sosfilt(butter(2, [f1, f2], 'band', fs=SR, output='sos'), x)


def put(buf, x, t0, gain=1.0):
    i0 = int(t0 * SR)
    if i0 >= len(buf):
        return
    n = min(len(x), len(buf) - i0)
    if n > 0:
        buf[i0:i0 + n] += x[:n] * gain


def env(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na > 0:
        e[:min(na, n)] = np.linspace(0, 1, min(na, n))
    if nr > 0 and nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def pad(freqs, dur, vol=1.0, a=1.4, r=1.8, bright=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        for dt in (-0.0035, 0.0, 0.0035):
            for h, amp in ((1, 1.0), (2, .5 * bright), (3, .33 * bright), (4, .2 * bright), (5, .12 * bright)):
                x += amp * np.sin(2 * np.pi * f * h * (1 + dt) * t + h * dt * 40) / (1 + 0.0)
    x *= (1 + 0.12 * np.sin(2 * np.pi * 0.23 * t))
    x /= max(1e-6, len(freqs) * 3)
    return x * env(n, a, r) * vol


def pluck(f, dur=1.4, vol=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * t) + .4 * np.sin(4 * np.pi * f * t) + .15 * np.sin(6 * np.pi * f * t)) * np.exp(-t * 4.5)
    return x * vol * env(n, 0.003, 0.05)


def piano(f, dur=3.0, vol=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * t) + .5 * np.sin(4 * np.pi * f * t) * np.exp(-t * 2) + .25 * np.sin(6 * np.pi * f * t) * np.exp(-t * 3)) * np.exp(-t * 1.4)
    return x * vol * env(n, 0.004, 0.2)


def kick(vol=1.0):
    n = int(.5 * SR)
    t = np.arange(n) / SR
    f = 120 * np.exp(-t * 18) + 38
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 8) * vol


def noise(n):
    return rng.normal(size=n)


# ------------------------------------------------------------------ narracao
narr = np.zeros(N)
for i in range(8):
    p = f'{TTS_DIR}/n{i}.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-ar', str(SR), '-ac', '1', f'{TTS_DIR}/m{i}.wav'], check=True)
    x, _ = sf.read(f'{TTS_DIR}/m{i}.wav')
    put(narr, x, ST[i] + NOFF[i], 1.0)
nenv = lp(np.abs(narr), 3.0, 2) * 3.0
nenv = np.clip(nenv, 0, 1)

# ------------------------------------------------------------------ musica
mus = np.zeros(N)
CH = {
    'Dm': [50, 53, 57], 'Bb': [46, 50, 53], 'F': [53, 57, 60], 'C': [48, 52, 55], 'Gm': [43, 46, 50], 'Am': [45, 48, 52],
}
# A: 0-17 misterio
prog = ['Dm', 'Bb', 'Dm', 'Gm']
t0 = 0.0
k = 0
while t0 < 40:
    name = prog[k % 4]
    notes = [mid(m + 12) for m in CH[name]]
    bass = [mid(CH[name][0] - 12)]
    d = 4.4
    vol = 0.55 + 0.45 * min(1, t0 / 30)
    put(mus, pad(notes, d + 1.5, vol=0.38 * vol, bright=0.6 + t0 / 40), t0)
    put(mus, pad(bass, d + 1.5, vol=0.5 * vol, bright=.3), t0)
    t0 += d
    k += 1
# B: 17-40 arpejo e batida crescendo
chords = ['Dm', 'Bb', 'F', 'C']
t = 17.0
j = 0
while t < 40:
    cname = chords[int((t - 17.0) // 4.4) % 4]
    ns = CH[cname]
    f = mid(ns[j % 3] + 24)
    prog_ = clamp = min(1.0, (t - 17) / 16)
    put(mus, pluck(f, 1.2, .16 + .22 * prog_), t)
    t += 0.3 if t < 31.8 else 0.15
    j += 1
tb = 24.0
while tb < 39.8:
    put(mus, kick(0.35 + .6 * min(1, (tb - 24) / 12)), tb)
    tb += 0.6 if tb < 31.8 else 0.45
# C: 40-50 contemplativo (maior)
prog2 = ['F', 'C', 'Dm', 'Bb', 'F']
t0 = 40.0
for q, name in enumerate(prog2):
    notes = [mid(m + 12) for m in CH.get(name, CH['F'])]
    put(mus, pad(notes, 5.5, vol=0.45, bright=0.9, a=1.8, r=2.0), t0)
    put(mus, pad([mid(CH.get(name, CH['F'])[0] - 12)], 5.5, vol=.5, bright=.3), t0)
    t0 += 4.2
mel = [(41.0, 72), (43.0, 76), (45.0, 79), (47.0, 77), (49.0, 76)]
for tt_, m in mel:
    put(mus, pad([mid(m)], 3.2, vol=0.35, a=.4, r=1.4, bright=.4), tt_)
# D: 50-57 piano esparso
for tt_, m in ((50.4, 62), (51.6, 69), (53.0, 65), (54.2, 72), (55.4, 70), (56.2, 74)):
    put(mus, piano(mid(m), 3.4, .5), tt_)
put(mus, pad([mid(50 + 12), mid(53 + 12), mid(57 + 12)], 8.0, vol=0.22, a=2.5, r=2.5, bright=.5), 50.0)
# E: 57-67 climax emocional + resolucao
prog3 = ['F', 'C', 'Bb', 'F']
t0 = 56.8
for q, name in enumerate(prog3):
    notes = [mid(m + 12) for m in CH[name]] + [mid(CH[name][0] + 24)]
    put(mus, pad(notes, 4.4, vol=0.7 - q * .04, bright=1.1, a=1.2, r=2.0), t0)
    put(mus, pad([mid(CH[name][0] - 12)], 4.4, vol=.6, bright=.3), t0)
    t0 += 2.6
for tt_, m in ((57.5, 81), (59.5, 79), (61.5, 77), (63.5, 76), (65.0, 72)):
    put(mus, pad([mid(m)], 3.0, vol=0.38, a=.3, r=1.5, bright=.5), tt_)
# reverb simples
ir = np.exp(-np.linspace(0, 5.5, int(2.6 * SR))) * rng.normal(size=int(2.6 * SR))
ir = lp(ir, 5000)
rev = fftconvolve(mus, ir[:int(2.6 * SR)] * 0.0035)[:N]
mus = mus * 0.7 + rev * 0.9
mus = lp(mus, 9000)

# ------------------------------------------------------------------ efeitos
sfx = np.zeros(N)
# vento espacial (continuo suave com LFO)
n = N
w = lp(noise(n), 500) * (0.5 + 0.5 * np.sin(2 * np.pi * np.arange(n) / SR * 0.07))
sfx += w * 0.12
# rastro do satelite (cena 1)
m = int(5.5 * SR)
sw = bp(noise(m), 800, 3500) * env(m, 1.5, 2.0) * 0.05
put(sfx, sw, ST[0] + 1.2)
# rádio: estatica e bips do Sputnik (cena 2)
t = ST[1] + 1.6
while t < ST[1] + 7.6:
    n_ = int(0.16 * SR)
    tt = np.arange(n_) / SR
    b = np.sin(2 * np.pi * 1000 * tt) * env(n_, 0.004, 0.02) * 0.16
    put(sfx, b, t)
    t += 0.62
m = int(7 * SR)
put(sfx, hp(noise(m), 2500) * env(m, .6, 1.0) * 0.035 * (0.6 + 0.4 * np.sin(np.arange(m) / SR * 7)), ST[1] + .6)
# estatica de rádio (cena 3, Gagarin)
m = int(5 * SR)
st3 = bp(noise(m), 600, 4500) * (np.random.default_rng(3).random(m // 2000 + 1).repeat(2000)[:m] > 0.55) * env(m, .2, .6) * 0.05
put(sfx, st3, ST[2] + .4)
# batidas de data (boom grave) em reveals
for tt_, g_ in ((ST[1] + .5, .7), (ST[2] + .4, .7), (ST[4] + .5, .6), (ST[5] + 4.0, .5), (ST[6] + 4.9, .6)):
    n_ = int(1.2 * SR)
    t_ = np.arange(n_) / SR
    f_ = 70 * np.exp(-t_ * 3) + 32
    b = np.sin(2 * np.pi * np.cumsum(f_) / SR) * np.exp(-t_ * 3.2) * g_ * 0.55
    put(sfx, b, tt_)
# motor/ruido crescente na plataforma (cena 4)
m = int(7.4 * SR)
hum = lp(noise(m), 120) * env(m, 3.0, 1.0) * 0.18 + np.sin(2 * np.pi * 55 * np.arange(m) / SR) * env(m, 3.0, 1.0) * 0.04
put(sfx, hum, ST[3] + .2)
# riser + lancamento (cena 5)
m = int(2.6 * SR)
rs = hp(noise(m), 1500) * (np.linspace(0, 1, m) ** 2) * 0.12
put(sfx, rs, ST[4] - 2.2)
ln = int(8.4 * SR)
tt = np.arange(ln) / SR
ru = lp(noise(ln), 220, 2) * 1.2 + bp(noise(ln), 300, 1800) * 0.5 * np.clip(tt / 2.5, 0, 1) + lp(noise(ln), 60, 2) * 1.5
ru *= np.clip(tt / 1.2, 0, 1) * np.where(tt > 6.5, np.clip(1 - (tt - 6.5) / 1.9, 0, 1), 1)
crackle = (np.random.default_rng(5).random(ln) > 0.9993) * rng.normal(size=ln) * 3
ru += lp(crackle, 4000) * 0.5
put(sfx, ru, ST[4] + .35, 0.36)
# vento/ar rapido no close (cena 5)
m = int(4.0 * SR)
put(sfx, bp(noise(m), 500, 5000) * env(m, 0.5, 1.5) * 0.07, ST[4] + 3.9)
# poeira, pouso (cena 6): retropropulsor e toque
m = int(6.6 * SR)
tt = np.arange(m) / SR
thr = bp(noise(m), 120, 1400) * 0.22 * env(m, 0.8, 0.6) + lp(noise(m), 90) * 0.16
put(sfx, thr, ST[5] + 0.4)
n_ = int(1.5 * SR)
t_ = np.arange(n_) / SR
thud = np.sin(2 * np.pi * np.cumsum(60 * np.exp(-t_ * 6) + 30) / SR) * np.exp(-t_ * 4) * 0.7 + lp(noise(n_), 900) * np.exp(-t_ * 5) * 0.25
put(sfx, thud, ST[5] + 6.4)
dh = hp(noise(int(2.4 * SR)), 1500) * env(int(2.4 * SR), 0.05, 2.0) * 0.06
put(sfx, dh, ST[5] + 6.45)
# primeiro passo (cena 7) + radio
n_ = int(0.9 * SR)
t_ = np.arange(n_) / SR
step = (lp(noise(n_), 600) * np.exp(-t_ * 10) * 0.8 + np.sin(2 * np.pi * 70 * t_) * np.exp(-t_ * 9) * 0.6)
put(sfx, step, ST[6] + 3.55)
rr = bp(noise(int(1.2 * SR)), 900, 3200) * env(int(1.2 * SR), 0.02, 0.4) * 0.05
put(sfx, rr, ST[6] + 0.6)
put(sfx, rr, ST[6] + 5.6)
# swoosh de transicao
for k_ in range(1, 8):
    m = int(.9 * SR)
    sw = bp(noise(m), 300, 6000) * np.sin(np.linspace(0, np.pi, m)) ** 2 * 0.06
    put(sfx, sw, ST[k_] - .45)
# fade final
sfx *= np.clip((TOTAL + 0.5 - np.arange(N) / SR) / 1.5, 0, 1)

# ------------------------------------------------------------------ mixagem
duck = 1.0 - 0.5 * nenv
mix_ = narr * 1.0 + mus * 0.55 * duck + sfx * 0.9 * (1.0 - 0.25 * nenv)
fade = np.clip((TOTAL + 1.0 - np.arange(N) / SR) / 1.8, 0, 1) * np.clip(np.arange(N) / SR / 0.5, 0, 1)
mix_ *= fade
peak = np.max(np.abs(mix_))
mix_ = mix_ / peak * 0.92
st = np.stack([mix_, mix_], axis=1)
# leve espacializacao estereo da musica/sfx
st[:, 0] = narr / peak * 0.92 + (mus * 0.55 * duck + sfx * 0.9) / peak * 0.92 * 1.0
st[:, 1] = narr / peak * 0.92 + (np.roll(mus, 220) * 0.55 * duck + np.roll(sfx, 90) * 0.9) / peak * 0.92 * 1.0
st *= fade[:, None]
sf.write(os.path.join(OUT_DIR, 'audio_mix.wav'), st.astype(np.float32), SR)
print('ok', N / SR)
