"""
PASSO 2 - Uma rede neural completa (a "cabeça" do carro)

Juntando vários neurônios em camadas temos uma rede neural:

   SENSORES  ->  CAMADA ESCONDIDA  ->  SAÍDA
   (7 + viés)      (6 + viés)          (2: volante e acelerador)

Esta é uma versão menor da rede do vídeo (18 sensores, 6 escondidos, 4 saídas).
A ideia é idêntica, só tem menos neurônios.

A segunda saída (o acelerador) é opcional: um genoma com uma saída só (campeões antigos,
de antes do experimento do freio e acelerador) continua funcionando, com velocidade fixa.

Tudo que a rede "sabe" cabe em uma lista de números: os pesos.
Isso é o "genoma" do carro. Na evolução, vamos copiar e mutar essa lista.

Rode:  python 02_rede.py
"""
import math
import random

N_SENSORES = 7
N_ESCONDIDOS = 6
N_SAIDAS = 2               # 0 = volante, 1 = acelerador (negativo freia, positivo acelera)

# quantos pesos existem no total (o +1 em cada camada é o viés)
N_PESOS = (N_SENSORES + 1) * N_ESCONDIDOS + (N_ESCONDIDOS + 1) * N_SAIDAS
N_PESOS_SO_VOLANTE = (N_SENSORES + 1) * N_ESCONDIDOS + (N_ESCONDIDOS + 1) * 1   # rede antiga: 1 saída


def saidas_do_genoma(pesos):
    """Quantas saídas a rede tem, deduzido do tamanho do genoma (1 = só volante, 2 = volante + acelerador)."""
    return (len(pesos) - (N_SENSORES + 1) * N_ESCONDIDOS) // (N_ESCONDIDOS + 1)


def genoma_valido(pesos):
    return len(pesos) in (N_PESOS, N_PESOS_SO_VOLANTE)


def relu(x):
    return max(0.0, x)


def pesos_aleatorios():
    return [random.uniform(-1, 1) for _ in range(N_PESOS)]


def pensar(pesos, sensores):
    """Recebe a lista de pesos e as leituras dos sensores. Devolve a lista de saídas (cada uma de -1 a 1):
    [volante] ou [volante, acelerador]."""
    entrada = list(sensores) + [1.0]  # o viés é uma entrada que vale sempre 1
    i = 0

    # camada escondida: cada neurônio olha para TODOS os sensores
    escondida = []
    for _ in range(N_ESCONDIDOS):
        soma = 0.0
        for valor in entrada:
            soma += valor * pesos[i]
            i += 1
        escondida.append(relu(soma))
    escondida.append(1.0)  # viés da próxima camada

    # camada de saída: cada neurônio olha para TODOS os escondidos
    saidas = []
    for _ in range(saidas_do_genoma(pesos)):
        soma = 0.0
        for valor in escondida:
            soma += valor * pesos[i]
            i += 1
        saidas.append(math.tanh(soma))  # tanh deixa a saída entre -1 e 1
    return saidas


if __name__ == "__main__":
    print(f"Esta rede tem {N_PESOS} pesos.\n")

    # Dois carros com cérebros aleatórios diferentes veem a MESMA situação:
    # parede muito perto à esquerda (sensores da esquerda baixos).
    situacao = [0.1, 0.2, 0.4, 0.8, 1.0, 1.0, 1.0]
    for nome in ["Carro A", "Carro B", "Carro C"]:
        genoma = pesos_aleatorios()
        volante, acelerador = pensar(genoma, situacao)
        lado = "direita" if volante > 0 else "esquerda"
        pedal = "acelera" if acelerador > 0 else "freia"
        print(f"{nome}: volante = {volante:+.2f} (vira para a {lado}) | acelerador = {acelerador:+.2f} ({pedal})")

    print("\nCada carro reage de um jeito porque os pesos são diferentes.")
    print("A maioria desses cérebros aleatórios dirige mal. A evolução vai achar os bons.")
