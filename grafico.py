"""
EXPERIMENTO E - Gráfico do aprendizado.

Desenha, com o próprio pygame (sem matplotlib), o quanto os carros avançaram
a cada geração:
  - verde: o MELHOR carro da geração
  - azul:  a MÉDIA de todos os carros da geração

O que observar: o melhor sobe rápido nas primeiras gerações e depois estabiliza
(platô). A média sobe mais devagar, porque a população ainda tem muitos mutantes
que erram.
"""
import pygame

COR_FUNDO = (35, 35, 42)
COR_BORDA = (110, 110, 125)
COR_TEXTO = (210, 210, 220)
COR_MELHOR = (90, 200, 120)
COR_MEDIA = (120, 160, 240)


def _pontos(valores, x0, x1, y0, y1, maximo):
    n = len(valores)
    return [
        (x0 + (x1 - x0) * (i / max(n - 1, 1)), y1 - (y1 - y0) * (v / maximo))
        for i, v in enumerate(valores)
    ]


def desenhar_grafico(tela, retangulo, melhores, medias, fonte):
    pygame.draw.rect(tela, COR_FUNDO, retangulo)
    pygame.draw.rect(tela, COR_BORDA, retangulo, 1)

    x0, x1 = retangulo.left + 30, retangulo.right - 8
    y0, y1 = retangulo.top + 22, retangulo.bottom - 16
    maximo = max(1.0, max(melhores, default=0.0))

    tela.blit(fonte.render("voltas por geração", True, COR_TEXTO), (retangulo.left + 6, retangulo.top + 3))
    tela.blit(fonte.render(f"{maximo:.1f}", True, COR_TEXTO), (retangulo.left + 3, y0 - 5))
    tela.blit(fonte.render("0", True, COR_TEXTO), (retangulo.left + 15, y1 - 8))
    tela.blit(fonte.render(f"gerações: {len(melhores)}", True, COR_TEXTO), (x0, retangulo.bottom - 14))
    pygame.draw.line(tela, COR_BORDA, (x0, y1), (x1, y1), 1)

    for valores, cor in ((medias, COR_MEDIA), (melhores, COR_MELHOR)):
        pontos = _pontos(valores, x0, x1, y0, y1, maximo)
        if len(pontos) >= 2:
            pygame.draw.lines(tela, cor, False, pontos, 2)
        elif pontos:
            pygame.draw.circle(tela, cor, (int(pontos[0][0]), int(pontos[0][1])), 3)


def salvar_png(caminho, melhores, medias):
    """Salva o gráfico em uma imagem maior, para guardar ou colocar no README."""
    pygame.font.init()
    fonte = pygame.font.SysFont("monospace", 14)
    imagem = pygame.Surface((640, 360))
    desenhar_grafico(imagem, imagem.get_rect(), melhores, medias, fonte)
    legenda_y = 4
    imagem.blit(fonte.render("verde = melhor   azul = média", True, COR_TEXTO), (400, legenda_y))
    pygame.image.save(imagem, caminho)
