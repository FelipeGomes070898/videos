"""Trilha, efeitos e mixagem da versao horizontal (13 cenas). Uso: ORIENT=h VIDEO_DIR=... python3 engine/audio_h.py"""
import os, sys, json, subprocess, numpy as np, soundfile as sf
from scipy.signal import fftconvolve
from synth import *
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO_DIR = os.environ['VIDEO_DIR']
OUT_DIR = os.environ.get('OUT_DIR', os.path.join(ROOT, 'out'))
TTS_DIR = os.path.join(OUT_DIR, 'tts')
sys.path.insert(0, VIDEO_DIR)
import scenes as SC
ST, DURS, TOTAL = SC.STARTS, SC.DURS, SC.TOTAL
OFF = SC.OFF
N = int((TOTAL + 2.0) * SR)
nsc = len(ST)

# narracao
narr = np.zeros(N)
for i in range(nsc):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{TTS_DIR}/n{i}.wav', '-ar', str(SR), '-ac', '1', f'{TTS_DIR}/m{i}.wav'], check=True)
    x, _ = sf.read(f'{TTS_DIR}/m{i}.wav')
    put(narr, x, ST[i] + OFF[i], 1.0)
nenv = np.clip(lp(np.abs(narr), 3.0, 2) * 3.0, 0, 1)

# musica
mus = np.zeros(N)
CH = {'Dm': [50, 53, 57], 'Bb': [46, 50, 53], 'F': [53, 57, 60], 'C': [48, 52, 55], 'Gm': [43, 46, 50], 'Am': [45, 48, 52]}
tA, tB, tC, tD, tE = 0.0, ST[3], ST[7], ST[9], ST[11]
launch = ST[6]
# A+B: misterio crescendo ate o lancamento
prog = ['Dm', 'Bb', 'Dm', 'Gm']
t0, k = 0.0, 0
while t0 < ST[7]:
    nm = prog[k % 4]
    vol = .5 + .5 * min(1, t0 / launch)
    put(mus, pad([mid(m + 12) for m in CH[nm]], 6.0, vol=.38 * vol, bright=.6 + min(1, t0 / launch)), t0)
    put(mus, pad([mid(CH[nm][0] - 12)], 6.0, vol=.5 * vol, bright=.3), t0)
    t0 += 4.6; k += 1
# arpejo entre B e o clímax
chords = ['Dm', 'Bb', 'F', 'C']
t = tB; j = 0
while t < ST[7]:
    nm = chords[int((t - tB) // 4.6) % 4]
    f = mid(CH[nm][j % 3] + 24)
    pr = min(1.0, (t - tB) / (launch - tB))
    put(mus, pluck(f, 1.2, .14 + .22 * pr), t)
    t += .32 if t < launch else .16
    j += 1
tb = tB + 10
while tb < ST[7]:
    put(mus, kick(.3 + .6 * min(1, (tb - tB - 10) / (launch - tB - 10))), tb)
    tb += .64 if tb < launch else .48
# C: contemplativo (viagem e pouso)
t0 = tC
for q, nm in enumerate(['F', 'C', 'Dm', 'Bb', 'F', 'C']):
    if t0 >= tD:
        break
    put(mus, pad([mid(m + 12) for m in CH[nm]], 6.0, vol=.45, bright=.9, a=1.8, r=2.0), t0)
    put(mus, pad([mid(CH[nm][0] - 12)], 6.0, vol=.5, bright=.3), t0)
    t0 += 4.6
for dt, m in ((2.0, 72), (6.5, 76), (11.0, 79), (15.5, 77), (19.5, 76)):
    if tC + dt < tD:
        put(mus, pad([mid(m)], 3.4, vol=.35, a=.4, r=1.4, bright=.4), tC + dt)
# D: piano esparso (passo e caminhada)
for dt, m in ((.8, 62), (2.4, 69), (4.2, 65), (6.0, 72), (7.8, 70), (9.6, 74), (12.0, 69), (14.4, 77), (17.0, 74), (19.6, 72)):
    if tD + dt < tE:
        put(mus, piano(mid(m), 3.6, .5), tD + dt)
put(mus, pad([mid(62), mid(65), mid(69)], tE - tD + 2, vol=.22, a=3.0, r=2.5, bright=.5), tD)
# E: climax emocional e resolucao
t0 = tE - 1.0
for q, nm in enumerate(['F', 'C', 'Bb', 'F', 'C', 'F']):
    notes = [mid(m + 12) for m in CH[nm]] + [mid(CH[nm][0] + 24)]
    put(mus, pad(notes, 6.0, vol=.7 - q * .03, bright=1.1, a=1.2, r=2.2), t0)
    put(mus, pad([mid(CH[nm][0] - 12)], 6.0, vol=.6, bright=.3), t0)
    t0 += 4.6
for dt, m in ((1.0, 81), (4.2, 79), (7.4, 77), (10.6, 76), (14.0, 72), (17.5, 69)):
    put(mus, pad([mid(m)], 3.4, vol=.38, a=.3, r=1.6, bright=.5), tE + dt)
ir = lp(np.exp(-np.linspace(0, 5.5, int(2.6 * SR))) * rng.normal(size=int(2.6 * SR)), 5000)
mus = lp(mus * .7 + fftconvolve(mus, ir * .0035)[:N] * .9, 9000)

# efeitos
sfx = np.zeros(N)
w = lp(noise(N), 500) * (.5 + .5 * np.sin(2 * np.pi * np.arange(N) / SR * .07))
sfx += w * .12
m = int(7 * SR); put(sfx, bp(noise(m), 800, 3500) * env(m, 2, 2.5) * .05, ST[0] + 1.5)
t = ST[1] + 1.4
while t < ST[1] + DURS[1] - 1.0:
    n_ = int(.16 * SR); tt = np.arange(n_) / SR
    put(sfx, np.sin(2 * np.pi * 1000 * tt) * env(n_, .004, .02) * .16, t); t += .62
m = int((DURS[1] - 1) * SR); put(sfx, hp(noise(m), 2500) * env(m, .6, 1) * .035, ST[1] + .6)
m = int(6 * SR)
put(sfx, bp(noise(m), 600, 4500) * (np.random.default_rng(3).random(m // 2000 + 1).repeat(2000)[:m] > .55) * env(m, .2, .6) * .05, ST[2] + .5)
bo = [ST[1] + .5, ST[2] + .3, ST[3] + .6, ST[5] + .5, ST[6] + .5, ST[8] + .8, ST[9] + DURS[9] * .52 + .5, ST[11] + .6, ST[12] + 3.0]
for tt_ in bo:
    n_ = int(1.2 * SR); t_ = np.arange(n_) / SR
    put(sfx, np.sin(2 * np.pi * np.cumsum(70 * np.exp(-t_ * 3) + 32) / SR) * np.exp(-t_ * 3.2) * .38, tt_)
m = int((DURS[4] - 1) * SR)
put(sfx, (lp(noise(m), 120) * env(m, 3, 1) * .18 + np.sin(2 * np.pi * 55 * np.arange(m) / SR) * env(m, 3, 1) * .04), ST[4] + .3)
m = int(2.8 * SR); put(sfx, hp(noise(m), 1500) * (np.linspace(0, 1, m) ** 2) * .12, ST[6] - 2.4)
cut = DURS[6] * .5
ln = int((DURS[6] - .5) * SR); tt = np.arange(ln) / SR
ru = lp(noise(ln), 220, 2) * 1.2 + bp(noise(ln), 300, 1800) * .5 * np.clip(tt / 2.5, 0, 1) + lp(noise(ln), 60, 2) * 1.5
ru *= np.clip(tt / 1.2, 0, 1) * np.where(tt > ln / SR - 2.0, np.clip((ln / SR - tt) / 2.0, 0, 1), 1)
ru += lp((np.random.default_rng(5).random(ln) > .9993) * rng.normal(size=ln) * 3, 4000) * .5
put(sfx, ru, ST[6] + 1.0, .36)
m = int((DURS[6] - cut - .5) * SR); put(sfx, bp(noise(m), 500, 5000) * env(m, .5, 1.5) * .07, ST[6] + cut)
m = int((DURS[7] - 1) * SR); put(sfx, lp(noise(m), 200) * env(m, 1.5, 1.5) * .05, ST[7] + .4)
touch = DURS[8] * .72
m = int(touch * SR)
put(sfx, bp(noise(m), 120, 1400) * .22 * env(m, .8, .6) + lp(noise(m), 90) * .16, ST[8] + .4)
for dt in (touch * .55, touch * .55 + .33, touch * .55 + .66):
    n_ = int(.12 * SR); put(sfx, np.sin(2 * np.pi * 1400 * np.arange(n_) / SR) * env(n_, .003, .03) * .1, ST[8] + dt)
n_ = int(1.5 * SR); t_ = np.arange(n_) / SR
put(sfx, np.sin(2 * np.pi * np.cumsum(60 * np.exp(-t_ * 6) + 30) / SR) * np.exp(-t_ * 4) * .7 + lp(noise(n_), 900) * np.exp(-t_ * 5) * .25, ST[8] + touch)
put(sfx, hp(noise(int(2.4 * SR)), 1500) * env(int(2.4 * SR), .05, 2) * .06, ST[8] + touch + .05)
d9 = DURS[9]; A_end = d9 * .28; B_end = d9 * .52; tch = A_end + (B_end - A_end) * .45
n_ = int(.9 * SR); t_ = np.arange(n_) / SR
put(sfx, lp(noise(n_), 600) * np.exp(-t_ * 10) * .8 + np.sin(2 * np.pi * 70 * t_) * np.exp(-t_ * 9) * .6, ST[9] + tch + .05)
rr = bp(noise(int(1.2 * SR)), 900, 3200) * env(int(1.2 * SR), .02, .4) * .05
for dt in (.6, B_end + 3.0):
    put(sfx, rr, ST[9] + dt)
m = int(5 * SR); put(sfx, bp(noise(m), 300, 3000) * env(m, 1.0, 1.5) * .04, ST[10] + 1.0)
land = DURS[11] * .62
m = int(land * SR); put(sfx, bp(noise(m), 200, 2500) * env(m, 1, 1.5) * .03, ST[11] + .5)
n_ = int(2.0 * SR); t_ = np.arange(n_) / SR
put(sfx, lp(noise(n_), 1200) * np.exp(-t_ * 2.5) * .5 + np.sin(2 * np.pi * np.cumsum(90 * np.exp(-t_ * 5) + 35) / SR) * np.exp(-t_ * 3) * .5, ST[11] + land)
for k_ in range(1, nsc):
    m = int(.9 * SR)
    put(sfx, bp(noise(m), 300, 6000) * np.sin(np.linspace(0, np.pi, m)) ** 2 * .06, ST[k_] - .45)

# mixagem
duck = 1.0 - .5 * nenv
fade = np.clip((TOTAL + 1.0 - np.arange(N) / SR) / 1.8, 0, 1) * np.clip(np.arange(N) / SR / .5, 0, 1)
mix_ = (narr + mus * .55 * duck + sfx * .9 * (1 - .25 * nenv)) * fade
peak = np.max(np.abs(mix_))
st = np.stack([narr + mus * .55 * duck + sfx * .9, narr + np.roll(mus, 220) * .55 * duck + np.roll(sfx, 90) * .9], axis=1) / peak * .92 * fade[:, None]
sf.write(os.path.join(OUT_DIR, 'audio_mix.wav'), st.astype(np.float32), SR)
print('ok', N / SR)
