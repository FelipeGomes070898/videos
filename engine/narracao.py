"""Gera a narracao (Kokoro-ONNX, voz pm_alex, pt-BR) e grava duracoes em dur.json.
Uso: python3 engine/narracao.py   (baixe kokoro.onnx e voices.bin, ver BRIEF.md)"""
import os, json, subprocess, soundfile as sf
from kokoro_onnx import Kokoro
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO_DIR = os.environ.get('VIDEO_DIR', os.path.join(ROOT, 'scenes', 'corrida_espacial'))
OUT = os.path.join(os.environ.get('OUT_DIR', os.path.join(ROOT, 'out')), 'tts')
MODEL = os.environ.get('KOKORO_DIR', OUT)
os.makedirs(OUT, exist_ok=True)
P = json.load(open(os.path.join(VIDEO_DIR, 'params.json')))
V = P['voz']
k = Kokoro(os.path.join(MODEL, 'kokoro.onnx'), os.path.join(MODEL, 'voices.bin'))
dur = []
for i, txt in enumerate(P['narracao']):
    s, sr = k.create(txt, voice=V['nome'], speed=V['velocidade'], lang=V['lang'])
    sf.write(f'{OUT}/raw{i}.wav', s, sr)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{OUT}/raw{i}.wav', '-af', V['filtro_ffmpeg'], f'{OUT}/n{i}.wav'], check=True)
    dur.append(round(sf.info(f'{OUT}/n{i}.wav').duration, 2))
json.dump(dur, open(os.path.join(VIDEO_DIR, 'dur.json'), 'w'))
print(dur, sum(dur))
