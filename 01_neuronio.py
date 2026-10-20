"""
PASSO 1 - Um único neurônio

Um neurônio artificial faz só três coisas:
  1. multiplica cada entrada pelo seu PESO
  2. soma tudo (mais o VIÉS)
  3. passa o resultado por uma função de ATIVAÇÃO

Os pesos são o que a rede "aprendeu". Aprender = encontrar bons pesos.

Rode:  python 01_neuronio.py
"""


def relu(x):
    # ReLU: se for negativo vira 0, se for positivo fica igual.
    # É a ativação usada no vídeo "Deep Cars".
    return max(0.0, x)


def neuronio(entradas, pesos, vies):
    soma = vies
    for entrada, peso in zip(entradas, pesos):
        soma += entrada * peso
    return relu(soma)


# Imagine um carro com 2 sensores: distância até a parede da esquerda e da direita.
# 0.0 = encostado na parede, 1.0 = parede bem longe.
esquerda = 0.2   # parede da esquerda está perto
direita = 0.9    # parede da direita está longe

# Pesos escolhidos À MÃO para este neurônio: "ligue se a esquerda está perto
# e a direita está longe" (ou seja, o carro deve virar para a direita).
pesos = [-1.0, 1.0]
vies = 0.0

saida = neuronio([esquerda, direita], pesos, vies)
print(f"entradas = esquerda {esquerda}, direita {direita}")
print(f"saída do neurônio = {saida:.2f}  (maior = mais vontade de virar à direita)")

# Teste você mesmo: troque os valores de esquerda/direita e rode de novo.
# Repare que, com pesos diferentes, o MESMO neurônio decidiria outra coisa.
# Na evolução, o computador testa pesos até achar os que dirigem bem.
