"""
O carro: sensores + cérebro (a rede do 02_rede.py) + movimento.

Usado tanto pelo treino (03_evolucao.py) quanto pelo teste em outra pista
(04_teste_em_outra_pista.py).
"""
import math
from importlib import import_module

from pista import CENTRO

rede = import_module("02_rede")  # reaproveita a rede do passo 2

VELOCIDADE = 4.0           # pixels por quadro (fixa: a rede só controla o volante)
VIRADA_MAX = 0.08          # radianos por quadro com o volante todo para um lado
ALCANCE_SENSOR = 150       # até onde o sensor enxerga
ANGULOS_SENSORES = [-90, -45, -20, 0, 20, 45, 90]  # graus, relativos à frente do carro

# a rede tem uma entrada por sensor: os dois números precisam andar juntos
assert rede.N_SENSORES == len(ANGULOS_SENSORES), "N_SENSORES (02_rede.py) != len(ANGULOS_SENSORES)"


class Carro:
    def __init__(self, genoma, pista):
        self.genoma = genoma
        self.pista = pista
        self.x, self.y = pista.largada()
        self.angulo = -math.pi / 2          # olhando para cima
        self.vivo = True
        self.quadros_vivo = 0
        self.progresso = 0.0                # radianos percorridos em volta da pista
        self.angulo_anterior = 0.0
        self.sensores = [1.0] * len(ANGULOS_SENSORES)

    @property
    def voltas(self):
        # abs: um carro que foi para o lado contrário também conta como avanço
        return abs(self.progresso) / (2 * math.pi)

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
                if not self.pista.na_pista(px, py):
                    break
                dist += passo
            leituras.append(dist / ALCANCE_SENSOR)
        self.sensores = leituras

    def atualizar(self):
        if not self.vivo:
            return
        self.quadros_vivo += 1
        self.ler_sensores()
        volante = rede.pensar(self.genoma, self.sensores)   # <- AQUI o cérebro decide

        self.angulo += volante * VIRADA_MAX
        self.x += math.cos(self.angulo) * VELOCIDADE
        self.y += math.sin(self.angulo) * VELOCIDADE

        if not self.pista.na_pista(self.x, self.y):
            self.vivo = False
            return

        # quanto o carro avançou ao redor do centro desde o quadro anterior?
        atual = math.atan2(self.y - CENTRO[1], self.x - CENTRO[0])
        delta = atual - self.angulo_anterior
        delta = (delta + math.pi) % (2 * math.pi) - math.pi  # corrige a volta de -pi para pi
        self.progresso += delta
        self.angulo_anterior = atual
