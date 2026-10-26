"""
O visual do carrinho, desenhado por código (sem imagens externas).

O carro é desenhado uma vez "deitado" (frente para a direita) e depois girado
conforme o ângulo. Os sensores amarelos saem dos pontos da carroceria definidos
em carro.py.
"""
import colorsys
import math

import pygame

from carro import COMPRIMENTO, LARGURA_CARRO

COR_MORTO = (80, 55, 55)
COR_APAGADO = (62, 62, 72)    # carros fora do top 10: aparecem, mas sem chamar atenção
_cache = {}


def cor_do_carro(indice):
    """Uma cor diferente para cada carro (a elite mantém a mesma cor entre gerações)."""
    r, g, b = colorsys.hsv_to_rgb((indice * 0.618) % 1.0, 0.65, 0.95)
    return int(r * 255), int(g * 255), int(b * 255)


def _base(cor):
    if cor in _cache:
        return _cache[cor]
    w, h = COMPRIMENTO, LARGURA_CARRO
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    escura = tuple(int(c * 0.55) for c in cor)
    vidro = (30, 42, 62)

    for x in (3, w - 9):                                      # rodas (aparecem nas pontas)
        pygame.draw.rect(s, (15, 15, 18), (x, 0, 6, 2))
        pygame.draw.rect(s, (15, 15, 18), (x, h - 2, 6, 2))
    pygame.draw.rect(s, cor, (1, 1, w - 2, h - 2), border_radius=4)   # carroceria
    pygame.draw.rect(s, vidro, (15, 3, 5, h - 6), border_radius=1)    # para-brisa
    pygame.draw.rect(s, escura, (9, 3, 6, h - 6))                      # teto
    pygame.draw.rect(s, vidro, (5, 3, 3, h - 6))                       # vidro traseiro
    pygame.draw.rect(s, (255, 240, 150), (w - 3, 2, 2, 3))             # faróis
    pygame.draw.rect(s, (255, 240, 150), (w - 3, h - 5, 2, 3))
    _cache[cor] = s
    return s


def desenhar_carro(tela, carro, cor, destaque=False):
    """Desenha o carro girado. Morto fica apagado; destaque pinta um anel branco em volta."""
    imagem = _base(cor if carro.vivo else COR_MORTO)
    girada = pygame.transform.rotate(imagem, -math.degrees(carro.angulo))
    tela.blit(girada, girada.get_rect(center=(int(carro.x), int(carro.y))))
    if destaque:
        pygame.draw.circle(tela, (255, 255, 255), (int(carro.x), int(carro.y)), 17, 1)


def desenhar_sensores(tela, carro):
    """As linhas amarelas que mostram o que o carro 'vê'."""
    for x0, y0, x1, y1 in carro.raios:
        pygame.draw.line(tela, (240, 220, 80), (x0, y0), (x1, y1), 1)
        pygame.draw.circle(tela, (255, 120, 60), (int(x0), int(y0)), 2)   # onde o sensor está preso
