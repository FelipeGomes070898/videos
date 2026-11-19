# HANDOFF — estado do projeto

Atualize este arquivo ao fim de cada sessão (máx. ~150 palavras no estado atual).

## Estado atual
- Corrida Espacial (9:16, 67 s, 8 cenas): pronto em 1080p e 4K, com e sem legenda.
  Cenas: Terra + satélite, Sputnik, cápsula do Gagarin em corte, Saturno V subindo, lançamento, pouso, passo, legado.
- Segunda Guerra (720x1280, 60 s, 7 cenas): versões 1, 2 e 3 (6 melhorias) prontas.
- Thumbnail: prompt escrito, imagem ainda não gerada.
- Texto de publicação do Facebook: pronto.

## CONCLUÍDO
- [x] Motor 2.5D copiado para `engine/` (common, main, audio, narracao, patch_segmento).
- [x] Roteiro, narração (texto), parâmetros e durações em `scenes/corrida_espacial/`.
- [x] Cenas 1, 5 e 7 renderizadas a partir deste repositório e comparadas com o original: idênticas pixel a pixel.

## PENDENTE
- [ ] Narração e áudio completo não foram rodados a partir do repositório (exigem baixar o modelo de voz, ver BRIEF.md).
- [ ] Thumbnail: gerar a imagem (prompt já escrito).

## Próximo passo
- Novo vídeo: criar `scenes/<nome>/` com `scenes.py`, `params.json`, `roteiro.md`, `narracao.txt` e rodar `engine/narracao.py`.

## Como começar um chat novo
Cole: "Leia BRIEF.md e HANDOFF.md do repositório videos e continue: <tarefa>".
