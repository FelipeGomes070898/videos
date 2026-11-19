# BRIEF — Série de documentários animados 2D (vertical)

Fonte de verdade do padrão visual e técnico. Leia este arquivo e o HANDOFF.md antes de qualquer cena.
Não releia nem peça o histórico de chats antigos.

## Formato
- Vertical 9:16, render em 1080x1920 (4K 2160x3840 só por upscale com ffmpeg, no final).
- Duração: 60–75 s por vídeo, 8 cenas.
- Entrega: versão 1080p e 4K; sem legendas queimadas por padrão (só datas e infográficos nas cenas).

## Estilo visual
- Ilustração vetorial 2D com profundidade 2.5D e parallax, desenhada por código.
- Formas geométricas limpas, sombras suaves, luz de contorno (rim light) laranja.
- Acabamento: bloom suave (ajustado por cena, forte demais lava cenas claras), grão de filme fino, vinheta leve.
- Câmera: zoom/travelling por cena; transições com zoom e flash.
- Evitar: logos reais, estilo fotográfico, rostos realistas, excesso de elementos, texto com erro de ortografia.

## Paleta
| Uso | Hex |
|---|---|
| Azul-marinho | #0E1838 |
| Preto espacial | #05070E |
| Bege | #E4D6BA |
| Branco | #F6F4EE |
| Cinza | #969CA8 |
| Laranja queimado (destaque) | #CE6428 |
| Amarelo suave | #F4D682 |

## Tipografia
- Sans-serif bold estilo Poppins Bold; mono discreta para legendas técnicas (ex.: "384.400 km").
- Alto contraste, margem de segurança de 80 px.

## Áudio
- Narração masculina em português do Brasil, mais grave. Conferir tom e ritmo ouvindo.
- Trilha sintetizada que cresce do mistério ao clímax.
- Efeitos por cena (rádio, bipes, rugido, passos etc.).
- Cenas ajustadas à duração da fala; total pode passar do roteiro original.

## Regras de produção
- Conteúdo 100% original, nada reaproveitado de vídeos anteriores.
- Não apagar versões anteriores; gerar arquivo novo a cada mudança grande.
- Grão de filme pesa no arquivo: comprimir ao final (ex.: 132 MB sem compressão).
- Renderizar direto em 4K leva mais de 1 h: renderizar em 1080p e ampliar.
- Mudanças: devolver só o trecho alterado, não o arquivo inteiro.

## Motor de animação
- Código em `engine/`: `common.py` (Terra/Lua procedurais, estrelas, câmera `G`, personagens), `main.py` (transições, pós-processamento, render), `audio.py` (trilha, efeitos, mixagem), `narracao.py` (voz), `patch_segmento.py` (re-renderiza só um trecho).
- Cada vídeo em `scenes/<nome-do-video>/`: `scenes.py` (cenas), `params.json`, `dur.json`, `roteiro.md`, `narracao.txt`.
- Vídeos renderizados ficam fora do Git (ver .gitignore).

## Comandos
- Teste de quadros: `python3 engine/main.py still 4,33,52` (saída em `out/`).
- Render completo: `python3 engine/main.py out/v1080.mp4 out/v4k.mp4` (gera 1080p e 4K por upscale, sem áudio, ~17 min com 2 núcleos).
- Narração: `python3 engine/narracao.py`, depois `python3 engine/audio.py` (gera `out/audio_mix.wav`).
- Variáveis: `VIDEO_DIR` (pasta do vídeo), `OUT_DIR`, `SUBS=1` (legenda queimada; padrão desligada).
- Dependências: pillow, numpy, scipy, soundfile, kokoro-onnx, ffmpeg, fontes Poppins e DejaVu Sans Mono.
- Modelo de voz: baixar `kokoro-v1.0.onnx` e `voices-v1.0.bin` em github.com/thewh1teagle/kokoro-onnx/releases (tag model-files-v1.0) e salvar como `out/tts/kokoro.onnx` e `out/tts/voices.bin`.

## Versão horizontal (YouTube 16:9)
- `ORIENT=h`: 1920x1080, 24 fps, 4K 3840x2160 por upscale. Pasta `scenes/corrida_espacial_16x9/` (13 cenas, ~175 s).
- Extra no pós: brilho anamórfico horizontal (azulado) além do bloom.
- Áudio: `ORIENT=h VIDEO_DIR=... OUT_DIR=... python3 engine/audio_h.py` (usa `engine/synth.py`).
- Exportação final: `-vf hqdn3d=3:3:6:6` antes do x264 (reduz muito o peso do grão): 1080p crf 22 (~74 MB), 4K crf 23 (~185 MB). Render completo ~35 min (4208 quadros, 2 núcleos).
- Exemplo: `ORIENT=h VIDEO_DIR=$PWD/scenes/corrida_espacial_16x9 OUT_DIR=$PWD/out python3 engine/narracao.py` e depois `engine/main.py out/v1080.mp4 out/v4k.mp4`.

## Valores do padrão (técnicos)
- fps 30; render 1080x1920; 4K por `scale=2160:3840:flags=lanczos`; vídeo 67 s (2010 quadros).
- Fontes: Poppins Bold (títulos e datas), Poppins Medium (subtítulos de data), DejaVu Sans Mono (rótulos técnicos). Legenda queimada (opcional): Poppins Bold 50 px, faixa escura no rodapé a partir de y=1620.
- Bloom: reduzir a 1/4, limiar 170 (×1,8), blur gaussiano 8, intensidade 0,35 (em cenas claras, reduzir ou zerar).
- Cor: contraste ×1,07 em torno de 128, tinta suave por cena (lista GRADE em `main.py`).
- Vinheta: 0,34 (elíptica, raio 0,74 da largura/altura). Textura de papel: multiplicador 0,965–1,015 estático.
- Grão de filme: ruído gaussiano sigma 2,6 por quadro. Fade de entrada 0,6 s e saída 1,0 s.
- Transições: 0,7 s, centradas no corte (íris com anel laranja, cortina com linha laranja, zoom com dissolução).
- Cenas: Terra procedural (textura 2048x1024, nuvens), sprite base 560 px reescalado; Lua procedural com crateras.
- Voz: Kokoro-ONNX, voz `pm_alex`, pt-br, velocidade 0,95; pós: tom -6% (asetrate 22560 + atempo 1,0638), realce de graves +4 dB em 120 Hz, compressor (-20 dB, 3:1), loudnorm -16 LUFS.
- Mixagem: narração 1,0; trilha 0,55 com redução de 50% sob a fala; efeitos 0,9; saída final loudnorm I=-16, TP=-1,5, LRA=9; AAC 192 kbps.
- Compressão final: 1080p crf 25, 4K crf 27 (preset medium). Não rodar duas codificações 4K em paralelo (falta de memória).
- Voz: não foi possível ouvir o resultado nesta sessão; conferir tom e ritmo.

## Metadados de publicação (Facebook)
- Sem campo de tags: palavras-chave no fim do texto, no máximo 5 hashtags.
- Estrutura: título com emoji, gancho, lista de marcos com emojis, pergunta para comentários, chamada para compartilhar e seguir.
- Thumbnail: mesmo estilo e camadas do vídeo, 9:16, título "CORRIDA" branco + "ESPACIAL" laranja.
