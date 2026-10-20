"""
PASSO 3 - Os carros aprendendo a dirigir (evolução com mutações aleatórias)

É o mesmo método do vídeo "Deep Cars". O ciclo de cada GERAÇÃO é:

  1. Todos os carros começam na largada, cada um com um cérebro (rede do passo 2).
  2. Cada carro lê seus sensores e vira o volante. Bateu na parede? Está fora.
  3. Pontuação (fitness) = o quanto o carro avançou na pista.
  4. Os MELHORES são copiados para a próxima geração, e os outros carros
     viram cópias deles com pequenas MUTAÇÕES nos pesos.
  5. Volta ao passo 1.

Ninguém ensina o carro a dirigir. Os bons genes só sobrevivem e se espalham.

Teclas:  ESPAÇO = modo turbo (acelera a simulação)   ESC = sair
Rode:    .venv/bin/python 03_evolucao.py
"""
import math
import random
import sys

import pygame

from importlib import import_module

rede = import_module("02_rede")  # reaproveita a rede do passo 2

# ----------------------------- configurações -----------------------------
LARGURA, ALTURA = 900, 700
CENTRO = (450, 350)
RAIO_MEDIO = 220           # raio do meio da pista
ONDULACAO = 55             # quanto a pista "balança" para dentro e para fora (cria curvas)
LARGURA_PISTA = 70
CURVAS = 4                 # quantas ondulações a pista tem

POPULACAO = 100            # quantos carros por geração (o vídeo usa 1000)
VELOCIDADE = 4.0           # pixels por quadro (fixa: a rede só controla o volante)
VIRADA_MAX = 0.08          # radianos por quadro com o volante todo para um lado
ALCANCE_SENSOR = 150       # até onde o sensor enxerga
ANGULOS_SENSORES = [-90, -45, -20, 0, 20, 45, 90]  # graus, relativos à frente do carro
MAX_QUADROS = 1800         # tempo máximo de uma geração

QTD_ELITE = 10             # quantos melhores passam direto para a próxima geração
CHANCE_MUTACAO = 0.15      # chance de CADA peso sofrer mutação
FORCA_MUTACAO = 0.3        # tamanho típico da mutação


# ------------------------------- a pista ---------------------------------
def raio_do_meio(angulo):
    # um círculo com ondulações: sem elas, bastaria virar o volante um pouco
    # para sempre para o mesmo lado e o carro daria voltas sem "pensar".
    return RAIO_MEDIO + ONDULACAO * math.sin(CURVAS * angulo)


def na_pista(x, y):
    distancia = math.hypot(x - CENTRO[0], y - CENTRO[1])
    angulo = math.atan2(y - CENTRO[1], x - CENTRO[0])
    return abs(distancia - raio_do_meio(angulo)) < LARGURA_PISTA / 2


def borda(lado):
    """Pontos de uma das bordas da pista (lado = +1 externa, -1 interna), para desenhar."""
    pontos = []
    for i in range(200):
        a = 2 * math.pi * i / 200
        r = raio_do_meio(a) + lado * LARGURA_PISTA / 2
        pontos.append((CENTRO[0] + r * math.cos(a), CENTRO[1] + r * math.sin(a)))
    return pontos


# -------------------------------- o carro --------------------------------
class Carro:
    def __init__(self, genoma):
        self.genoma = genoma
        self.x = CENTRO[0] + raio_do_meio(0.0)
        self.y = CENTRO[1]
        self.angulo = -math.pi / 2          # olhando para cima
        self.vivo = True
        self.progresso = 0.0                # radianos percorridos em volta da pista
        self.angulo_anterior = 0.0
        self.sensores = [1.0] * len(ANGULOS_SENSORES)

    def ler_sensores(self):
        """Lança um raio por sensor e mede a distância até a parede (0 a 1)."""
        leituras = []
        for graus in ANGULOS_SENSORES:
            direcao = self.angulo + math.radians(graus)
            passo = 5
            dist = 0
            while dist < ALCANCE_SENSOR:
                px = self.x + math.cos(direcao) * dist
                py = self.y + math.sin(direcao) * dist
                if not na_pista(px, py):
                    break
                dist += passo
            leituras.append(dist / ALCANCE_SENSOR)
        self.sensores = leituras

    def atualizar(self):
        if not self.vivo:
            return
        self.ler_sensores()
        volante = rede.pensar(self.genoma, self.sensores)   # <- AQUI o cérebro decide

        self.angulo += volante * VIRADA_MAX
        self.x += math.cos(self.angulo) * VELOCIDADE
        self.y += math.sin(self.angulo) * VELOCIDADE

        if not na_pista(self.x, self.y):
            self.vivo = False
            return

        # quanto o carro avançou ao redor do centro desde o quadro anterior?
        atual = math.atan2(self.y - CENTRO[1], self.x - CENTRO[0])
        delta = atual - self.angulo_anterior
        delta = (delta + math.pi) % (2 * math.pi) - math.pi  # corrige a volta de -pi para pi
        self.progresso += delta
        self.angulo_anterior = atual


# ------------------------------- evolução --------------------------------
def mutar(genoma):
    novo = []
    for peso in genoma:
        if random.random() < CHANCE_MUTACAO:
            peso += random.gauss(0, FORCA_MUTACAO)
        novo.append(peso)
    return novo


def proxima_geracao(carros):
    # ordena do que mais avançou (progresso negativo = foi para o lado errado)
    ordenados = sorted(carros, key=lambda c: abs(c.progresso), reverse=True)
    elite = [c.genoma for c in ordenados[:QTD_ELITE]]

    novos = [list(g) for g in elite]               # a elite passa sem mutação
    while len(novos) < POPULACAO:
        pai = random.choice(elite)                 # cópia mutada de um dos melhores
        novos.append(mutar(pai))
    return [Carro(g) for g in novos]


# ------------------------------ desenho/loop -----------------------------
def desenhar(tela, fonte, carros, geracao, recorde, quadro):
    tela.fill((25, 25, 30))
    pygame.draw.polygon(tela, (70, 70, 80), borda(+1))
    pygame.draw.polygon(tela, (25, 25, 30), borda(-1))

    vivos = [c for c in carros if c.vivo]
    melhor = max(carros, key=lambda c: abs(c.progresso))

    for c in carros:
        cor = (90, 200, 120) if c.vivo else (110, 60, 60)
        pygame.draw.circle(tela, cor, (int(c.x), int(c.y)), 4 if c.vivo else 2)

    # mostra os sensores do melhor carro vivo, para entender o que ele "vê"
    if melhor.vivo:
        for graus, leitura in zip(ANGULOS_SENSORES, melhor.sensores):
            d = math.radians(graus) + melhor.angulo
            fim = (melhor.x + math.cos(d) * leitura * ALCANCE_SENSOR,
                   melhor.y + math.sin(d) * leitura * ALCANCE_SENSOR)
            pygame.draw.line(tela, (240, 220, 80), (melhor.x, melhor.y), fim, 1)
        pygame.draw.circle(tela, (255, 255, 255), (int(melhor.x), int(melhor.y)), 6, 2)

    voltas = abs(melhor.progresso) / (2 * math.pi)
    linhas = [
        f"Geração: {geracao}",
        f"Carros vivos: {len(vivos)}/{len(carros)}",
        f"Melhor desta geração: {voltas:.2f} voltas",
        f"Recorde geral: {recorde:.2f} voltas",
        f"Quadro: {quadro}/{MAX_QUADROS}",
        "ESPAÇO = turbo | ESC = sair",
    ]
    for i, texto in enumerate(linhas):
        tela.blit(fonte.render(texto, True, (230, 230, 230)), (12, 10 + i * 22))
    pygame.display.flip()


def main(max_geracoes=None):
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Passo 3 - Carros evoluindo")
    fonte = pygame.font.SysFont("monospace", 16)
    relogio = pygame.time.Clock()

    carros = [Carro(rede.pesos_aleatorios()) for _ in range(POPULACAO)]
    geracao, quadro, recorde, turbo = 1, 0, 0.0, False

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return
                if evento.key == pygame.K_SPACE:
                    turbo = not turbo

        for _ in range(10 if turbo else 1):
            for c in carros:
                c.atualizar()
            quadro += 1

            melhor_voltas = max(abs(c.progresso) for c in carros) / (2 * math.pi)
            recorde = max(recorde, melhor_voltas)

            if quadro >= MAX_QUADROS or not any(c.vivo for c in carros):
                print(f"Geração {geracao:3d} | melhor: {melhor_voltas:.2f} voltas | recorde: {recorde:.2f}")
                if max_geracoes and geracao >= max_geracoes:
                    return
                carros = proxima_geracao(carros)
                geracao += 1
                quadro = 0
                break

        desenhar(tela, fonte, carros, geracao, recorde, quadro)
        relogio.tick(60)


if __name__ == "__main__":
    # "python 03_evolucao.py 5" roda só 5 gerações (útil para testar sem janela)
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
    pygame.quit()
