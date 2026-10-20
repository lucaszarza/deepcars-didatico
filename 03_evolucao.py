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

O que este script grava em resultados/ (veja a pasta depois de rodar):
  - campeao.json            o melhor carro até agora (experimento A)
  - historico.csv           nota de cada geração (experimento E)
  - curva_aprendizado.png   o gráfico final (experimento E)

Teclas:  ESPAÇO = modo turbo (acelera a simulação)   ESC = sair

Rode:    .venv/bin/python 03_evolucao.py
Opções:  --geracoes N     para depois de N gerações
         --pista NOME     treina em outra pista (veja pista.py)
         --sem-janela     treina sem desenhar, muito mais rápido
"""
import argparse
import csv
import math
import os
import random

import pygame

import genoma_io
import grafico
from carro import ALCANCE_SENSOR, ANGULOS_SENSORES, Carro, rede
from pista import PISTAS

# ----------------------------- configurações -----------------------------
LARGURA, ALTURA = 900, 700

POPULACAO = 100            # quantos carros por geração (o vídeo usa 1000)
MAX_QUADROS = 1800         # tempo máximo de uma geração

QTD_ELITE = 10             # quantos melhores passam direto para a próxima geração
CHANCE_MUTACAO = 0.15      # chance de CADA peso sofrer mutação
FORCA_MUTACAO = 0.3        # tamanho típico da mutação

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
CAMINHO_CAMPEAO = os.path.join(PASTA, "campeao.json")
CAMINHO_HISTORICO = os.path.join(PASTA, "historico.csv")
CAMINHO_GRAFICO = os.path.join(PASTA, "curva_aprendizado.png")


# ------------------------------- evolução --------------------------------
def mutar(genoma):
    novo = []
    for peso in genoma:
        if random.random() < CHANCE_MUTACAO:
            peso += random.gauss(0, FORCA_MUTACAO)
        novo.append(peso)
    return novo


def proxima_geracao(carros, pista):
    ordenados = sorted(carros, key=lambda c: c.voltas, reverse=True)
    elite = [c.genoma for c in ordenados[:QTD_ELITE]]

    novos = [list(g) for g in elite]               # a elite passa sem mutação
    while len(novos) < POPULACAO:
        pai = random.choice(elite)                 # cópia mutada de um dos melhores
        novos.append(mutar(pai))
    return [Carro(g, pista) for g in novos]


# ------------------------------ desenho/loop -----------------------------
def desenhar(tela, fonte, fonte_pequena, pista, carros, geracao, recorde, quadro, hist_melhor, hist_media):
    tela.fill((25, 25, 30))
    pista.desenhar(tela)

    melhor = max(carros, key=lambda c: c.voltas)
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

    linhas = [
        f"Pista: {pista.nome}",
        f"Geração: {geracao}",
        f"Carros vivos: {sum(c.vivo for c in carros)}/{len(carros)}",
        f"Melhor desta geração: {melhor.voltas:.2f} voltas",
        f"Recorde geral: {recorde:.2f} voltas",
        f"Quadro: {quadro}/{MAX_QUADROS}",
        "ESPAÇO = turbo | ESC = sair",
    ]
    for i, texto in enumerate(linhas):
        tela.blit(fonte.render(texto, True, (230, 230, 230)), (12, 10 + i * 22))

    grafico.desenhar_grafico(tela, pygame.Rect(8, 582, 200, 110), hist_melhor, hist_media, fonte_pequena)
    pygame.display.flip()


def main(args):
    pista = PISTAS[args.pista]
    os.makedirs(PASTA, exist_ok=True)

    tela = None
    if not args.sem_janela:
        pygame.init()
        tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Passo 3 - Carros evoluindo")
    pygame.font.init()
    fonte = pygame.font.SysFont("monospace", 16)
    fonte_pequena = pygame.font.SysFont("monospace", 11)
    relogio = pygame.time.Clock()

    carros = [Carro(rede.pesos_aleatorios(), pista) for _ in range(POPULACAO)]
    geracao, quadro, recorde, turbo = 1, 0, 0.0, False
    hist_melhor, hist_media = [], []

    with open(CAMINHO_HISTORICO, "w", newline="", encoding="utf-8") as arq_csv:
        escritor = csv.writer(arq_csv)
        escritor.writerow(["geracao", "melhor_voltas", "media_voltas"])

        try:
            while True:
                if tela is not None:
                    for evento in pygame.event.get():
                        if evento.type == pygame.QUIT:
                            return
                        if evento.type == pygame.KEYDOWN:
                            if evento.key == pygame.K_ESCAPE:
                                return
                            if evento.key == pygame.K_SPACE:
                                turbo = not turbo

                for _ in range(10 if (turbo or tela is None) else 1):
                    for c in carros:
                        c.atualizar()
                    quadro += 1

                    if quadro >= MAX_QUADROS or not any(c.vivo for c in carros):
                        melhor = max(carros, key=lambda c: c.voltas)
                        media = sum(c.voltas for c in carros) / len(carros)
                        hist_melhor.append(melhor.voltas)
                        hist_media.append(media)
                        escritor.writerow([geracao, f"{melhor.voltas:.3f}", f"{media:.3f}"])
                        arq_csv.flush()

                        if melhor.voltas > recorde:           # EXPERIMENTO A: guarda o campeão
                            recorde = melhor.voltas
                            genoma_io.salvar_campeao(
                                CAMINHO_CAMPEAO, melhor.genoma,
                                geracao=geracao, voltas=round(melhor.voltas, 3), pista=pista.nome,
                            )
                        print(f"Geração {geracao:3d} | melhor: {melhor.voltas:.2f} voltas | "
                              f"média: {media:.2f} | recorde: {recorde:.2f}", flush=True)

                        if args.geracoes and geracao >= args.geracoes:
                            return
                        carros = proxima_geracao(carros, pista)
                        geracao += 1
                        quadro = 0
                        break

                if tela is not None:
                    desenhar(tela, fonte, fonte_pequena, pista, carros, geracao, recorde,
                             quadro, hist_melhor, hist_media)
                    relogio.tick(60)
        finally:
            if hist_melhor:
                grafico.salvar_png(CAMINHO_GRAFICO, hist_melhor, hist_media)   # EXPERIMENTO E
                print(f"\nSalvo em {PASTA}/: campeao.json, historico.csv, curva_aprendizado.png")


if __name__ == "__main__":
    analisador = argparse.ArgumentParser(description="Carros evoluindo (passo 3)")
    analisador.add_argument("--geracoes", type=int, default=0, help="para depois de N gerações")
    analisador.add_argument("--pista", choices=list(PISTAS), default="treino", help="pista de treino")
    analisador.add_argument("--sem-janela", action="store_true", help="treina sem desenhar (rápido)")
    main(analisador.parse_args())
    pygame.quit()
