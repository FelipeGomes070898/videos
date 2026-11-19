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
- Código em `engine/` (a copiar do chat da Corrida Espacial, ver HANDOFF.md).
- Cenas em `scenes/<nome-do-video>/`.
- Vídeos renderizados ficam fora do Git (ver .gitignore).

## Metadados de publicação (Facebook)
- Sem campo de tags: palavras-chave no fim do texto, no máximo 5 hashtags.
- Estrutura: título com emoji, gancho, lista de marcos com emojis, pergunta para comentários, chamada para compartilhar e seguir.
- Thumbnail: mesmo estilo e camadas do vídeo, 9:16, título "CORRIDA" branco + "ESPACIAL" laranja.
