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

PISTAS ALEATÓRIAS (experimento D): com --aleatorias N, a cada geração são sorteadas N pistas
novas. O cérebro nunca vê duas vezes a mesma pista, então não tem padrão fixo para decorar.
No fim, a elite passa por uma VALIDAÇÃO: corre em pistas novas e o campeão é o que for melhor
nelas. Sem isso, o "melhor da última geração" costuma ser só um mutante com sorte nas
duas pistas daquela geração.

TREINAR EM VÁRIAS PISTAS (experimento C): com --pistas a, b, c, cada cérebro corre
em TODAS essas pistas ao mesmo tempo, e a nota é a MÉDIA das voltas. Assim ele não
consegue "decorar" uma pista só. Depois teste em pistas que ficaram de fora
(04_teste_em_outra_pista.py) para ver se ele generalizou.

O que este script grava em resultados/ (veja a pasta depois de rodar):
  - campeao.json            o melhor cérebro até agora (experimento A)
  - historico.csv           nota de cada geração (experimento E)
  - curva_aprendizado.png   o gráfico final (experimento E)

Teclas:  ESPAÇO = modo turbo   TAB = troca a pista que aparece na tela   ESC = sair

Rode:    .venv/bin/python 03_evolucao.py
Opções:  --geracoes N          para depois de N gerações
         --pistas a,b,c        pistas de treino, separadas por vírgula (veja pista.py)
         --aleatorias N        sorteia N pistas novas a cada geração (ignora --pistas)
         --autodromos N        como --aleatorias, mas com circuitos de autódromo (circuito.py)
         --dificeis            com --autodromos: circuitos mais travados e estreitos
         --largura-min PX      largura mínima das pistas sorteadas (padrão 60 nos anéis, 55 nos autódromos)
         --sem-janela          treina sem desenhar, muito mais rápido
         --turbo               abre a janela já em modo turbo
Exemplo: .venv/bin/python 03_evolucao.py --pistas treino,suave,muitas_curvas
"""
import argparse
import csv
import os
import random

import pygame

import genoma_io
import grafico
import sprite
from carro import Carro, rede
from circuito import DIFICIL, circuito_aleatorio
from pista import PISTAS, pista_aleatoria

# ----------------------------- configurações -----------------------------
LARGURA, ALTURA = 900, 700

POPULACAO = 100            # quantos cérebros por geração (o vídeo usa 1000)
MAX_QUADROS = 1800         # tempo máximo de uma geração

QTD_ELITE = 10             # quantos melhores passam direto para a próxima geração
CHANCE_MUTACAO = 0.15      # chance de CADA peso sofrer mutação
FORCA_MUTACAO = 0.3        # tamanho típico da mutação

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
CAMINHO_CAMPEAO = os.path.join(PASTA, "campeao.json")
CAMINHO_HISTORICO = os.path.join(PASTA, "historico.csv")
CAMINHO_GRAFICO = os.path.join(PASTA, "curva_aprendizado.png")


# ------------------------------- evolução --------------------------------
def criar_grupos(genomas, pistas):
    """Um grupo de carros por pista; o carro i de cada grupo usa o cérebro i."""
    return [[Carro(g, pista) for g in genomas] for pista in pistas]


def notas(grupos):
    """Nota de cada cérebro = média das voltas dele nas pistas de treino."""
    return [sum(grupo[i].voltas for grupo in grupos) / len(grupos) for i in range(len(grupos[0]))]


def mutar(genoma):
    novo = []
    for peso in genoma:
        if random.random() < CHANCE_MUTACAO:
            peso += random.gauss(0, FORCA_MUTACAO)
        novo.append(peso)
    return novo


def escolher_por_validacao(elite, quantidade=12):
    """Testa cada cérebro da elite em pistas NOVAS (nunca vistas) e devolve o melhor.

    É o "conjunto de validação" do aprendizado de máquina: a nota do treino pode ser
    sorte, a nota em dados novos mostra quem realmente generalizou.
    """
    pistas_val = sortear_pistas(quantidade)
    resultados = []
    for genoma in elite:
        carros = [Carro(genoma, p) for p in pistas_val]
        for _ in range(MAX_QUADROS):
            if not any(c.vivo for c in carros):
                break
            for c in carros:
                c.atualizar()
        media = sum(c.voltas for c in carros) / len(carros)
        completou = sum(c.vivo for c in carros)      # vivo ao fim = aguentou o tempo todo
        resultados.append((media, completou, genoma))
        print(f"  cérebro {len(resultados):2d}: {completou:2d}/{quantidade} pistas novas completas "
              f"(média {media:.2f} voltas)", flush=True)
    return max(resultados, key=lambda r: r[0]), quantidade


def proxima_geracao(genomas, pontos):
    ordem = sorted(range(len(genomas)), key=lambda i: pontos[i], reverse=True)
    elite = [genomas[i] for i in ordem[:QTD_ELITE]]

    novos = [list(g) for g in elite]               # a elite passa sem mutação
    while len(novos) < POPULACAO:
        pai = random.choice(elite)                 # cópia mutada de um dos melhores
        novos.append(mutar(pai))
    return novos


# ------------------------------ desenho/loop -----------------------------
def desenhar(tela, fonte, fonte_pequena, pistas, visivel, grupos, geracao, recorde, quadro,
             hist_melhor, hist_media):
    pista, carros = pistas[visivel], grupos[visivel]
    tela.fill((25, 25, 30))
    pista.desenhar(tela)

    melhor = max(carros, key=lambda c: c.voltas)
    for i, c in enumerate(carros):
        sprite.desenhar_carro(tela, c, sprite.cor_do_carro(i), destaque=(c is melhor))

    # mostra os sensores do melhor carro vivo, para entender o que ele "vê"
    if melhor.vivo:
        sprite.desenhar_sensores(tela, melhor)

    linhas = [
        f"Pista: {pista.nome} ({visivel + 1}/{len(pistas)})" + ("  TAB troca" if len(pistas) > 1 else ""),
        f"Geração: {geracao}",
        f"Carros vivos: {sum(c.vivo for c in carros)}/{len(carros)}",
        f"Melhor nesta pista: {melhor.voltas:.2f} voltas  (vel. {melhor.velocidade:.1f})",
        f"Recorde (nota média): {recorde:.2f} voltas",
        f"Quadro: {quadro}/{MAX_QUADROS}",
        "ESPAÇO = turbo | ESC = sair",
    ]
    for i, texto in enumerate(linhas):
        tela.blit(fonte.render(texto, True, (230, 230, 230)), (12, 10 + i * 22))

    grafico.desenhar_grafico(tela, pygame.Rect(8, 582, 200, 110), hist_melhor, hist_media, fonte_pequena)
    pygame.display.flip()


def main(args):
    pistas = sortear_pistas(args.aleatorias) if args.aleatorias else [PISTAS[nome] for nome in args.pistas]
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

    genomas = [rede.pesos_aleatorios() for _ in range(POPULACAO)]
    grupos = criar_grupos(genomas, pistas)
    geracao, quadro, recorde, turbo, visivel = 1, 0, 0.0, args.turbo, 0
    hist_melhor, hist_media, elite_atual = [], [], []

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
                            if evento.key == pygame.K_TAB:
                                visivel = (visivel + 1) % len(pistas)

                for _ in range(10 if (turbo or tela is None) else 1):
                    for grupo in grupos:
                        for c in grupo:
                            c.atualizar()
                    quadro += 1

                    if quadro >= MAX_QUADROS or not any(c.vivo for grupo in grupos for c in grupo):
                        pontos = notas(grupos)
                        i_melhor = max(range(POPULACAO), key=lambda i: pontos[i])
                        melhor_nota = pontos[i_melhor]
                        media = sum(pontos) / len(pontos)
                        ordem = sorted(range(POPULACAO), key=lambda i: pontos[i], reverse=True)
                        elite_atual = [genomas[i] for i in ordem[:QTD_ELITE]]
                        hist_melhor.append(melhor_nota)
                        hist_media.append(media)
                        escritor.writerow([geracao, f"{melhor_nota:.3f}", f"{media:.3f}"])
                        arq_csv.flush()

                        # EXPERIMENTO A: guarda o campeão. Com pistas aleatórias a pista muda a cada
                        # geração, então o recorde não é comparável: guarda o melhor da geração atual.
                        if args.aleatorias or melhor_nota > recorde:
                            recorde = max(recorde, melhor_nota)
                            genoma_io.salvar_campeao(
                                CAMINHO_CAMPEAO, genomas[i_melhor],
                                geracao=geracao, voltas=round(melhor_nota, 3),
                                pistas=[TIPO_SORTEIO] if args.aleatorias else [p.nome for p in pistas],
                            )
                        por_pista = " | ".join(
                            f"{p.nome} {grupo[i_melhor].voltas:.2f}" for p, grupo in zip(pistas, grupos))
                        print(f"Geração {geracao:3d} | nota: {melhor_nota:.2f} (média da pop.: {media:.2f}) "
                              f"| melhor cérebro por pista: {por_pista}", flush=True)

                        if args.geracoes and geracao >= args.geracoes:
                            return
                        genomas = proxima_geracao(genomas, pontos)
                        if args.aleatorias:
                            pistas = sortear_pistas(args.aleatorias)
                            visivel = min(visivel, len(pistas) - 1)
                        grupos = criar_grupos(genomas, pistas)
                        geracao += 1
                        quadro = 0
                        break

                if tela is not None:
                    desenhar(tela, fonte, fonte_pequena, pistas, visivel, grupos, geracao, recorde,
                             quadro, hist_melhor, hist_media)
                    relogio.tick(60)
        finally:
            if args.aleatorias and elite_atual:
                print("\nValidação: a elite corre em pistas novas...", flush=True)
                (media, completou, genoma), total = escolher_por_validacao(elite_atual)
                genoma_io.salvar_campeao(
                    CAMINHO_CAMPEAO, genoma, geracao=geracao, voltas=round(media, 3),
                    pistas=[TIPO_SORTEIO], validacao=f"{completou}/{total} pistas novas completas",
                )
                print(f"Campeão escolhido pela validação: {completou}/{total} pistas novas completas")
            if hist_melhor:
                grafico.salvar_png(CAMINHO_GRAFICO, hist_melhor, hist_media)   # EXPERIMENTO E
                print(f"\nSalvo em {PASTA}/: campeao.json, historico.csv, curva_aprendizado.png")


LARGURA_MIN_SORTEIO = None     # largura mínima das pistas sorteadas (--largura-min); None = padrão de cada tipo
AUTODROMO_DIFICIL = False      # --dificeis: circuitos mais travados e estreitos
TIPO_SORTEIO = "aleatorias"    # "aleatorias" = anéis ondulados, "autodromos" = circuitos (--autodromos)


def sortear_pistas(quantidade):
    if TIPO_SORTEIO == "autodromos":
        opcoes = dict(DIFICIL) if AUTODROMO_DIFICIL else {}
        if LARGURA_MIN_SORTEIO:
            opcoes["largura_min"] = LARGURA_MIN_SORTEIO
        return [circuito_aleatorio(f"sorteada_{i + 1}", **opcoes) for i in range(quantidade)]
    return [pista_aleatoria(f"sorteada_{i + 1}", LARGURA_MIN_SORTEIO or 60) for i in range(quantidade)]


def lista_de_pistas(texto):
    nomes = [n.strip() for n in texto.split(",") if n.strip()]
    for nome in nomes:
        if nome not in PISTAS:
            raise argparse.ArgumentTypeError(f"pista '{nome}' não existe. Opções: {', '.join(PISTAS)}")
    return nomes


if __name__ == "__main__":
    analisador = argparse.ArgumentParser(description="Carros evoluindo (passo 3)")
    analisador.add_argument("--geracoes", type=int, default=0, help="para depois de N gerações")
    analisador.add_argument("--pistas", type=lista_de_pistas, default=["treino"],
                            help="pistas de treino, separadas por vírgula (padrão: treino)")
    analisador.add_argument("--aleatorias", type=int, default=0, metavar="N",
                            help="sorteia N pistas novas a cada geração (ignora --pistas)")
    analisador.add_argument("--autodromos", type=int, default=0, metavar="N",
                            help="como --aleatorias, mas sorteia N circuitos de autódromo (retas, grampos, chicanes)")
    analisador.add_argument("--dificeis", action="store_true",
                            help="com --autodromos: circuitos com mais curvas, curvas no limite do carro e asfalto estreito")
    analisador.add_argument("--largura-min", type=int, default=None, metavar="PX",
                            help="largura mínima das pistas sorteadas (padrão: 60 nos anéis, 55 nos autódromos)")
    analisador.add_argument("--sem-janela", action="store_true", help="treina sem desenhar (rápido)")
    analisador.add_argument("--turbo", action="store_true", help="já começa em modo turbo (ESPAÇO alterna)")
    argumentos = analisador.parse_args()
    LARGURA_MIN_SORTEIO = argumentos.largura_min
    if argumentos.autodromos:
        TIPO_SORTEIO = "autodromos"
        AUTODROMO_DIFICIL = argumentos.dificeis
        argumentos.aleatorias = argumentos.autodromos
    main(argumentos)
    pygame.quit()
