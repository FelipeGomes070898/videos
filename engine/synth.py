"""Sintese sonora compartilhada (pads, plucks, piano, kick, filtros)."""
import numpy as np
from scipy.signal import butter, sosfilt
SR = 44100
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


