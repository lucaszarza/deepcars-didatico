"""
Circuitos de autódromo: retas, curvas fechadas, chicanes.

Diferente do anel ondulado de pista.py, aqui o traçado é uma curva fechada
qualquer. Como ela é criada:

  1. sorteiam-se alguns PONTOS DE CONTROLE espalhados em volta do centro da tela
  2. uma curva suave (spline de Catmull-Rom) passa por todos eles
  3. a curva tem as dobras impossíveis abertas e é reamostrada em pontos igualmente espaçados: a LINHA DO MEIO
  4. o asfalto é tudo que está a menos de largura/2 dessa linha
  5. circuitos impossíveis são descartados: curva mais fechada do que o carro
     consegue fazer, ou trechos do traçado que se encostam

O Circuito tem a mesma interface da Pista (na_pista, largada, desenhar...),
então o carro e o treino funcionam com os dois sem mudar.
"""
import math
import random

import pygame

LARGURA_TELA, ALTURA_TELA = 900, 700
PASSO = 3.0               # distância entre os pontos da linha do meio (pixels)
JANELA_BUSCA = 25         # quantos pontos para cada lado o carro procura sua posição

# O carro anda 4 px por quadro e vira no máximo 0,08 rad: o menor raio de curva dele é
# 4 / 0,08 = 50 px. Curvas da linha do meio mais fechadas que isso não dá para fazer.
RAIO_MIN_PADRAO = 70


def _catmull_rom(pontos, por_segmento=24):
    """Curva suave e fechada que passa por todos os pontos de controle."""
    n = len(pontos)
    saida = []
    for i in range(n):
        p0, p1, p2, p3 = pontos[(i - 1) % n], pontos[i], pontos[(i + 1) % n], pontos[(i + 2) % n]
        for k in range(por_segmento):
            t = k / por_segmento
            t2, t3 = t * t, t * t * t
            saida.append(tuple(
                0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t
                       + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                       + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)
                for j in (0, 1)))
    return saida


def _reamostrar(pontos, passo):
    """Troca os pontos por outros igualmente espaçados ao longo da curva."""
    n = len(pontos)
    comprimento = [0.0]
    for i in range(n):
        a, b = pontos[i], pontos[(i + 1) % n]
        comprimento.append(comprimento[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = comprimento[-1]
    quantidade = max(8, int(total / passo))
    saida, i = [], 0
    for k in range(quantidade):
        alvo = total * k / quantidade
        while comprimento[i + 1] < alvo:
            i += 1
        a, b = pontos[i], pontos[(i + 1) % n]
        f = (alvo - comprimento[i]) / max(comprimento[i + 1] - comprimento[i], 1e-9)
        saida.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
    return saida


def _aliviar_curvas(linha, raio_min, voltas_max=300):
    """Abre só as curvas fechadas demais, e deixa as outras como estão.

    A curva sorteada passa exatamente pelos pontos de controle e às vezes faz uma dobra que
    o carro não consegue fazer. Onde o raio é menor que raio_min, os pontos são puxados para
    a média dos vizinhos, repetidas vezes, até a curva ficar possível. As curvas que já eram
    possíveis não mudam, então sobram grampos e chicanes no limite do que o carro faz.
    """
    n = len(linha)
    for _ in range(voltas_max):
        ruins = set()
        for i in range(n):
            a, b, c = linha[(i - 6) % n], linha[i], linha[(i + 6) % n]
            area2 = abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1]))
            if area2 > 1e-9 and math.dist(a, b) * math.dist(b, c) * math.dist(c, a) / (2 * area2) < raio_min * 1.04:
                ruins.update((i + d) % n for d in range(-4, 5))
        if not ruins:
            break
        linha = [((linha[(i - 3) % n][0] + 2 * linha[i][0] + linha[(i + 3) % n][0]) / 4,
                  (linha[(i - 3) % n][1] + 2 * linha[i][1] + linha[(i + 3) % n][1]) / 4) if i in ruins else linha[i]
                 for i in range(n)]
    return _reamostrar(linha, PASSO)


def _raio_minimo(linha, abertura=6):
    """Menor raio de curva da linha do meio (círculo que passa por 3 pontos vizinhos)."""
    n, menor = len(linha), float("inf")
    for i in range(n):
        a, b, c = linha[(i - abertura) % n], linha[i], linha[(i + abertura) % n]
        ab, bc, ca = math.dist(a, b), math.dist(b, c), math.dist(c, a)
        area2 = abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1]))   # 2 x área
        if area2 > 1e-9:
            menor = min(menor, ab * bc * ca / (2 * area2))
    return menor


def _trechos_se_encostam(linha, largura):
    """True se duas partes distantes do traçado ficam perto demais (o asfalto se juntaria)."""
    passo_amostra = 3
    amostra = linha[::passo_amostra]
    n = len(amostra)
    distancia_pista = passo_amostra * PASSO
    for i in range(n):
        for j in range(i + 1, n):
            along = min(j - i, n - (j - i)) * distancia_pista
            if along > 4 * largura and math.dist(amostra[i], amostra[j]) < largura + 14:
                return True
    return False


def _dentro_da_tela(linha, largura):
    m = largura / 2 + 6
    return all(m <= x <= LARGURA_TELA - m and m <= y <= ALTURA_TELA - m for x, y in linha)


class Circuito:
    angulo_largada = 0.0     # preenchido no __init__

    def __init__(self, nome, linha, largura):
        self.nome = nome
        self.linha = linha          # pontos da linha do meio
        self.largura = largura
        self.n = len(linha)
        self.curvas = None

        a, b = linha[0], linha[2]
        self.angulo_largada = math.atan2(b[1] - a[1], b[0] - a[0])

        raio = int(largura / 2)
        mascara = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        mascara.set_colorkey((0, 0, 0))
        for x, y in linha:
            pygame.draw.circle(mascara, (255, 255, 255), (int(x), int(y)), raio)
        self._mascara = pygame.mask.from_surface(mascara)
        self._imagem = self._montar_imagem(raio)

    # ---- interface igual à da Pista ----
    def na_pista(self, x, y):
        xi, yi = int(x), int(y)
        if 0 <= xi < LARGURA_TELA and 0 <= yi < ALTURA_TELA:
            return bool(self._mascara.get_at((xi, yi)))
        return False

    def largada(self):
        return self.linha[0]

    def fase(self, x, y, anterior):
        """Onde o carro está ao longo do circuito, como um ângulo de 0 a 2π (uma volta = 2π).

        Procura só perto de onde ele estava no quadro anterior: é barato e não confunde
        dois trechos do traçado que passam perto um do outro.
        """
        centro = int(anterior / (2 * math.pi) * self.n) % self.n
        melhor, melhor_d = centro, float("inf")
        for k in range(-JANELA_BUSCA, JANELA_BUSCA + 1):
            i = (centro + k) % self.n
            px, py = self.linha[i]
            d = (px - x) ** 2 + (py - y) ** 2
            if d < melhor_d:
                melhor, melhor_d = i, d
        return 2 * math.pi * melhor / self.n

    def desenhar(self, tela):
        tela.blit(self._imagem, (0, 0))

    # ---- desenho ----
    def _montar_imagem(self, raio):
        imagem = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        imagem.set_colorkey((0, 0, 0))
        for x, y in self.linha:                                     # zebra (borda clara)
            pygame.draw.circle(imagem, (190, 190, 200), (int(x), int(y)), raio + 2)
        for x, y in self.linha:                                     # asfalto
            pygame.draw.circle(imagem, (70, 70, 80), (int(x), int(y)), raio)
        for i in range(0, self.n, 14):                              # tracejado do meio
            for k in range(i, min(i + 5, self.n)):
                x, y = self.linha[k]
                pygame.draw.circle(imagem, (110, 110, 120), (int(x), int(y)), 1)
        a, b = self.linha[0], self.linha[2]                         # linha de largada
        ang = math.atan2(b[1] - a[1], b[0] - a[0]) + math.pi / 2
        dx, dy = math.cos(ang) * raio, math.sin(ang) * raio
        pygame.draw.line(imagem, (240, 240, 240), (a[0] - dx, a[1] - dy), (a[0] + dx, a[1] + dy), 4)
        return imagem


def circuito_aleatorio(nome, largura_min=55, largura_max=90, raio_min=RAIO_MIN_PADRAO, sorteio=random,
                       pontos=(8, 14), tamanho_min=0.3):
    """Sorteia um circuito válido (tenta várias vezes até um passar nos testes)."""
    for _ in range(500):
        n = sorteio.randint(*pontos)
        controle = []
        for i in range(n):
            angulo = 2 * math.pi * (i + sorteio.uniform(-0.3, 0.3)) / n
            tamanho = sorteio.uniform(tamanho_min, 1.0)
            controle.append((450 + 360 * tamanho * math.cos(angulo), 350 + 260 * tamanho * math.sin(angulo)))
        linha = _aliviar_curvas(_reamostrar(_catmull_rom(controle), PASSO), raio_min)
        largura = sorteio.uniform(largura_min, largura_max)
        if (_dentro_da_tela(linha, largura) and _raio_minimo(linha) >= raio_min
                and not _trechos_se_encostam(linha, largura)):
            return Circuito(nome, linha, largura)
    raise RuntimeError("não consegui sortear um circuito válido")


# Autódromo "difícil": mais pontos de controle (mais curvas), curvas no limite do carro
# (raio 56, o carro faz no mínimo 50) e asfalto estreito.
DIFICIL = dict(largura_min=46, largura_max=64, raio_min=56, pontos=(11, 16), tamanho_min=0.22)


def circuito_fixo(nome, semente, **opcoes):
    """Um circuito que é sempre o mesmo (sorteado com uma semente fixa)."""
    return circuito_aleatorio(nome, sorteio=random.Random(semente), **opcoes)


_CACHE = {}


def circuitos_fixos(dificil=False):
    """Os 5 circuitos de teste (sempre os mesmos). Criados na primeira chamada, depois reaproveitados."""
    if dificil not in _CACHE:
        opcoes = DIFICIL if dificil else {}
        prefixo = "dificil" if dificil else "autodromo"
        sementes = [2, 3, 5, 6, 1] if dificil else [3, 7, 11, 21, 42]
        _CACHE[dificil] = {f"{prefixo}_{i}": circuito_fixo(f"{prefixo}_{i}", s, **opcoes)
                           for i, s in enumerate(sementes, start=1)}
    return _CACHE[dificil]
