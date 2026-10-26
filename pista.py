"""
As pistas.

Toda pista é um anel com ondulações. O raio do centro da pista muda conforme
o ângulo em volta do centro da tela:

    raio(ângulo) = RAIO_MEDIO + ONDULACAO * cos(CURVAS * ângulo)

  - ONDULACAO: o quanto a pista "balança" para dentro e para fora (curvas mais fortes)
  - CURVAS:    quantas ondulações cabem em uma volta
  - LARGURA:   a largura do asfalto (mais estreita = mais difícil)

Sem ondulação (círculo perfeito), bastaria virar o volante um pouco para o mesmo
lado, sempre, e o carro daria voltas sem "pensar". As ondulações obrigam o carro
a reagir ao que os sensores veem.

A pista "treino" é onde os carros aprendem (03_evolucao.py). As outras são
pistas que o campeão nunca viu, usadas no teste de generalização
(04_teste_em_outra_pista.py).
"""
import math
import random

import pygame

CENTRO = (450, 350)


class Pista:
    angulo_largada = -math.pi / 2   # o carro larga olhando para cima

    def __init__(self, nome, raio_medio, ondulacao, largura, curvas):
        self.nome = nome
        self.raio_medio = raio_medio
        self.ondulacao = ondulacao
        self.largura = largura
        self.curvas = curvas

    def raio_do_meio(self, angulo):
        return self.raio_medio + self.ondulacao * math.cos(self.curvas * angulo)

    def na_pista(self, x, y):
        distancia = math.hypot(x - CENTRO[0], y - CENTRO[1])
        angulo = math.atan2(y - CENTRO[1], x - CENTRO[0])
        return abs(distancia - self.raio_do_meio(angulo)) < self.largura / 2

    def fase(self, x, y, anterior):
        """Onde o carro está ao longo da pista, como ângulo em volta do centro (uma volta = 2π)."""
        return math.atan2(y - CENTRO[1], x - CENTRO[0])

    def largada(self):
        # em ângulo 0 o cosseno vale 1: o carro larga no ponto mais externo,
        # onde o rumo da pista é exatamente "para cima", o mesmo do carro.
        return CENTRO[0] + self.raio_do_meio(0.0), CENTRO[1]

    def borda(self, lado):
        """Pontos de uma das bordas (lado = +1 externa, -1 interna), para desenhar."""
        pontos = []
        for i in range(240):
            a = 2 * math.pi * i / 240
            r = self.raio_do_meio(a) + lado * self.largura / 2
            pontos.append((CENTRO[0] + r * math.cos(a), CENTRO[1] + r * math.sin(a)))
        return pontos

    def desenhar(self, tela):
        pygame.draw.polygon(tela, (70, 70, 80), self.borda(+1))
        pygame.draw.polygon(tela, (25, 25, 30), self.borda(-1))


PISTAS = {p.nome: p for p in [
    #     nome             raio  ondul. larg. curvas
    Pista("treino",        220,  55,    70,   4),   # onde os carros aprendem
    Pista("suave",         220,  40,    90,   3),   # menos curvas, mais larga
    Pista("muitas_curvas", 220,  30,    70,   6),   # curvas mais frequentes
    Pista("estreita",      220,  55,    50,   4),   # mesmo formato do treino, menos espaço
    Pista("dificil",       215,  50,    60,   5),   # curvas fortes e frequentes
]}


def pista_aleatoria(nome, largura_min=60):
    """Sorteia uma pista nova, com formato parecido com as fixas (mas nunca igual).

    Os limites evitam pistas impossíveis: quanto mais curvas, menor a ondulação, e
    a largura nunca fica estreita demais para o carro (largura_min).
    """
    curvas = random.randint(3, 6)
    return Pista(
        nome,
        raio_medio=random.uniform(205, 225),
        ondulacao=random.uniform(25, min(60, 200 / curvas)),
        largura=random.uniform(largura_min, 95),
        curvas=curvas,
    )
