"""
PASSO 4 - O campeão em uma pista que ele nunca viu (generalização)

O campeão aprendeu a dirigir na pista "treino". A pergunta agora é:
ele aprendeu A DIRIGIR, ou só DECOROU aquela pista?

  - Se ele vai bem em pistas novas, o que ele aprendeu serve em outras situações.
    Isso se chama GENERALIZAÇÃO e é o objetivo real de todo aprendizado de máquina.
  - Se ele só vai bem na pista de treino, houve OVERFITTING (sobreajuste):
    o modelo decorou o treino e não aprendeu a regra.

Para comparar, cada pista também recebe 100 carros com cérebro ALEATÓRIO (sem
treino nenhum). Eles mostram o "piso": o que se consegue sem aprender nada.
Atenção: com sorte, um ou outro cérebro aleatório aguenta uma pista fácil. Por isso
o relatório conta QUANTOS aguentam, e não só o melhor deles.

Rode (precisa de um campeão, veja abaixo):
    .venv/bin/python 04_teste_em_outra_pista.py                  janela com as pistas
    .venv/bin/python 04_teste_em_outra_pista.py --relatorio      tabela no terminal
    .venv/bin/python 04_teste_em_outra_pista.py outro_campeao.json

O campeão usado é, nesta ordem:
    1. o arquivo passado na linha de comando
    2. resultados/campeao.json         (criado por 03_evolucao.py)
    3. exemplos/campeao_exemplo.json   (já vem no repositório, se existir)

Teclas da janela:  1 a 5 = troca de pista | R = recomeça | ESPAÇO = turbo | ESC = sair
"""
import argparse
import os
import random
import sys

import pygame

import genoma_io
import sprite
from carro import Carro, rede
from pista import PISTAS

LARGURA, ALTURA = 900, 700
MAX_QUADROS = 1800        # o mesmo tempo máximo do treino
N_ALEATORIOS = 30         # carros "sem treino" desenhados na janela
N_BASE = 100              # carros aleatórios usados na tabela do relatório

AQUI = os.path.dirname(os.path.abspath(__file__))
CANDIDATOS = [
    os.path.join(AQUI, "resultados", "campeao.json"),
    os.path.join(AQUI, "exemplos", "campeao_exemplo.json"),
]


def achar_campeao(caminho):
    if caminho:
        return caminho
    for candidato in CANDIDATOS:
        if os.path.exists(candidato):
            return candidato
    return None


def correr(genoma, pista):
    """Um carro, uma pista, sem janela. Devolve o carro no fim da corrida."""
    carro = Carro(genoma, pista)
    for _ in range(MAX_QUADROS):
        if not carro.vivo:
            break
        carro.atualizar()
    return carro


def descrever(carro):
    if carro.vivo:
        return f"aguentou o tempo todo, {carro.voltas:.2f} voltas"
    return f"bateu no quadro {carro.quadros_vivo}, {carro.voltas:.2f} voltas"


# ------------------------------- relatório -------------------------------
def relatorio(genoma, info):
    random.seed(1)  # a comparação com os aleatórios fica repetível
    print(f"Campeão: {info}\n")
    # campeões antigos guardam só "pista"; os novos guardam a lista "pistas"
    treinadas = info.get("pistas") or [info.get("pista")]
    print(f"{'pista':<14} | {'campeão':<36} | aleatórios que aguentaram (de {N_BASE})")
    print("-" * 88)
    for pista in PISTAS.values():
        campeao = correr(genoma, pista)
        # conta quantos cérebros SEM treino aguentam o tempo todo: com sorte alguns
        # aguentam, por isso o número de sobreviventes diz mais que "o melhor deles"
        aguentaram = sum(correr(rede.pesos_aleatorios(), pista).vivo for _ in range(N_BASE))
        marca = "  (usada no treino)" if pista.nome in treinadas else "  (inédita)"
        print(f"{pista.nome:<14} | {descrever(campeao):<36} | {aguentaram}{marca}", flush=True)


# --------------------------------- janela --------------------------------
def nova_corrida(genoma, pista):
    campeao = Carro(genoma, pista)
    aleatorios = [Carro(rede.pesos_aleatorios(), pista) for _ in range(N_ALEATORIOS)]
    return campeao, aleatorios


def desenhar(tela, fonte, pistas, indice, campeao, aleatorios, quadro, turbo):
    pista = pistas[indice]
    tela.fill((25, 25, 30))
    pista.desenhar(tela)

    for c in aleatorios:
        sprite.desenhar_carro(tela, c, (130, 130, 140))      # sem treino: carros cinza

    if campeao.vivo:
        sprite.desenhar_sensores(tela, campeao)
    sprite.desenhar_carro(tela, campeao, (90, 220, 130), destaque=True)   # campeão: verde

    if campeao.vivo and quadro < MAX_QUADROS:
        situacao = "correndo..."
    else:
        situacao = descrever(campeao)

    linhas = [
        f"Pista {indice + 1}/{len(pistas)}: {pista.nome}",
        f"Campeão: {situacao}",
        f"Aleatórios vivos: {sum(c.vivo for c in aleatorios)}/{len(aleatorios)}",
        f"Quadro: {min(quadro, MAX_QUADROS)}/{MAX_QUADROS}" + ("   TURBO" if turbo else ""),
        "verde = campeão | cinza = sem treino",
        f"1-{len(pistas)} troca de pista | R recomeça | ESPAÇO turbo | ESC sai",
    ]
    for i, texto in enumerate(linhas):
        tela.blit(fonte.render(texto, True, (230, 230, 230)), (12, 10 + i * 22))
    pygame.display.flip()


def janela(genoma, info, pista_inicial):
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Passo 4 - Campeão em outra pista")
    fonte = pygame.font.SysFont("monospace", 16)
    relogio = pygame.time.Clock()

    pistas = list(PISTAS.values())
    indice = list(PISTAS).index(pista_inicial)
    campeao, aleatorios = nova_corrida(genoma, pistas[indice])
    quadro, turbo = 0, False

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return
                if evento.key == pygame.K_SPACE:
                    turbo = not turbo
                if evento.key == pygame.K_r:
                    campeao, aleatorios = nova_corrida(genoma, pistas[indice])
                    quadro = 0
                tecla = evento.key - pygame.K_1
                if 0 <= tecla < len(pistas):
                    indice = tecla
                    campeao, aleatorios = nova_corrida(genoma, pistas[indice])
                    quadro = 0

        for _ in range(5 if turbo else 1):
            if quadro < MAX_QUADROS and campeao.vivo:
                campeao.atualizar()
                for c in aleatorios:
                    c.atualizar()
                quadro += 1

        desenhar(tela, fonte, pistas, indice, campeao, aleatorios, quadro, turbo)
        relogio.tick(60)


if __name__ == "__main__":
    analisador = argparse.ArgumentParser(description="Campeão em outra pista (passo 4)")
    analisador.add_argument("campeao", nargs="?", help="arquivo .json do campeão")
    analisador.add_argument("--relatorio", action="store_true", help="tabela no terminal, sem janela")
    analisador.add_argument("--pista", choices=list(PISTAS), default="suave", help="pista inicial da janela")
    argumentos = analisador.parse_args()

    caminho = achar_campeao(argumentos.campeao)
    if caminho is None or not os.path.exists(caminho):
        sys.exit("Nenhum campeão encontrado. Rode antes: .venv/bin/python 03_evolucao.py")

    genoma, info = genoma_io.carregar_campeao(caminho)
    print(f"Usando {caminho}")
    if argumentos.relatorio:
        relatorio(genoma, info)
    else:
        janela(genoma, info, argumentos.pista)
        pygame.quit()
