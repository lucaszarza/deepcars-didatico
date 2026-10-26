"""
O carro: sensores + cérebro (a rede do 02_rede.py) + movimento.

Usado tanto pelo treino (03_evolucao.py) quanto pelo teste em outra pista
(04_teste_em_outra_pista.py).

O carro tem um corpo de COMPRIMENTO x LARGURA_CARRO pixels. Os sensores ficam
presos na carroceria (quinas, para-choque e laterais), como num carro de verdade,
e a batida vale para o corpo inteiro (as quatro quinas), não só para o centro.
"""
import math
from importlib import import_module


rede = import_module("02_rede")  # reaproveita a rede do passo 2

VELOCIDADE = 4.0           # pixels por quadro: velocidade fixa (rede antiga) e velocidade de largada
VEL_MIN, VEL_MAX = 1.5, 8.0   # limites quando a rede controla o acelerador
ACELERACAO = 0.15          # quanto a velocidade muda por quadro com o pedal todo apertado
VIRADA_MAX = 0.08          # radianos por quadro com o volante todo para um lado
ALCANCE_SENSOR = 150       # até onde o sensor enxerga

COMPRIMENTO, LARGURA_CARRO = 26, 13

# Cada sensor: (frente, direita, graus)
#   frente, direita = onde ele está preso, medido a partir do centro do carro (pixels)
#   graus           = para onde aponta, relativo à frente do carro (negativo = esquerda)
SENSORES = [
    (0, -6.5, -90),     # lateral esquerda
    (11, -6.5, -45),    # quina dianteira esquerda
    (13, -3, -20),      # para-choque, lado esquerdo
    (13, 0, 0),         # para-choque, centro
    (13, 3, 20),        # para-choque, lado direito
    (11, 6.5, 45),      # quina dianteira direita
    (0, 6.5, 90),       # lateral direita
]

# as quatro quinas do corpo (frente, direita), para detectar batida
QUINAS = [(13, -6.5), (13, 6.5), (-13, 6.5), (-13, -6.5)]

# a rede tem uma entrada por sensor: os dois números precisam andar juntos
assert rede.N_SENSORES == len(SENSORES), "N_SENSORES (02_rede.py) != len(SENSORES)"


class Carro:
    def __init__(self, genoma, pista):
        self.genoma = genoma
        self.pista = pista
        self.x, self.y = pista.largada()
        self.angulo = pista.angulo_largada  # olhando na direção da pista
        self.velocidade = VELOCIDADE
        self.vivo = True
        self.quadros_vivo = 0
        self.progresso = 0.0                # radianos percorridos em volta da pista
        self.angulo_anterior = 0.0
        self.sensores = [1.0] * len(SENSORES)
        self.raios = []                     # (x_ini, y_ini, x_fim, y_fim) de cada sensor, para desenhar

    @property
    def voltas(self):
        # abs: um carro que foi para o lado contrário também conta como avanço
        return abs(self.progresso) / (2 * math.pi)

    def _ponto(self, frente, direita):
        """Converte um ponto do corpo do carro (frente, direita) em coordenadas da tela."""
        c, s = math.cos(self.angulo), math.sin(self.angulo)
        return self.x + c * frente - s * direita, self.y + s * frente + c * direita

    def ler_sensores(self):
        """Cada sensor lança um raio a partir do seu ponto na carroceria e mede a distância até a parede (0 a 1)."""
        leituras = []
        self.raios = []
        for frente, direita, graus in SENSORES:
            ox, oy = self._ponto(frente, direita)
            direcao = self.angulo + math.radians(graus)
            passo = 5
            dist = 0
            while dist < ALCANCE_SENSOR:
                px = ox + math.cos(direcao) * dist
                py = oy + math.sin(direcao) * dist
                if not self.pista.na_pista(px, py):
                    break
                dist += passo
            leituras.append(dist / ALCANCE_SENSOR)
            self.raios.append((ox, oy, ox + math.cos(direcao) * dist, oy + math.sin(direcao) * dist))
        self.sensores = leituras

    def atualizar(self):
        if not self.vivo:
            return
        self.quadros_vivo += 1
        self.ler_sensores()
        saidas = rede.pensar(self.genoma, self.sensores)    # <- AQUI o cérebro decide
        volante = saidas[0]
        if len(saidas) > 1:                                 # a segunda saída é o acelerador (freio se negativo)
            self.velocidade = min(VEL_MAX, max(VEL_MIN, self.velocidade + saidas[1] * ACELERACAO))

        # a curva mais fechada que o carro faz tem raio = velocidade / VIRADA_MAX: quanto mais
        # rápido, mais aberta a curva. Para fazer curva fechada é preciso frear.
        self.angulo += volante * VIRADA_MAX
        self.x += math.cos(self.angulo) * self.velocidade
        self.y += math.sin(self.angulo) * self.velocidade

        # bateu se QUALQUER quina do corpo saiu do asfalto
        if not all(self.pista.na_pista(*self._ponto(f, d)) for f, d in QUINAS):
            self.vivo = False
            return

        # quanto o carro avançou ao longo da pista desde o quadro anterior? (a pista diz a posição dele)
        atual = self.pista.fase(self.x, self.y, self.angulo_anterior)
        delta = atual - self.angulo_anterior
        delta = (delta + math.pi) % (2 * math.pi) - math.pi  # corrige a volta de -pi para pi
        self.progresso += delta
        self.angulo_anterior = atual
