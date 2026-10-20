# Deepcars didático

Carros que aprendem a dirigir sozinhos, por evolução. Cada carro tem uma pequena rede neural; os que chegam mais longe passam seus "genes" adiante, com pequenas mutações. Em poucas gerações os carros completam a pista.

É uma versão didática, em Python, do vídeo [Deep Cars (Universo Programado)](https://www.youtube.com/watch?v=gnfkfUQvKDw). O código original, em C, é [JVictorDias/DeepCars](https://github.com/JVictorDias/DeepCars).

> Quer entender **por que** isso funciona? Leia a [TEORIA.md](TEORIA.md).

## Requisitos

- Python 3 (testado com 3.14)
- `pygame` (o único pacote externo)

## Instalação

```bash
git clone https://github.com/lucaszarza/deepcars-didatico.git
cd deepcars-didatico
python3 -m venv .venv
.venv/bin/pip install pygame
```

No Windows, use `.venv\Scripts\pip` e `.venv\Scripts\python` no lugar dos caminhos acima.

## Como rodar

Os arquivos são numerados para serem lidos e executados em ordem:

| Arquivo | O que faz | Comando |
|---|---|---|
| `01_neuronio.py` | Um neurônio, com as contas na tela | `python3 01_neuronio.py` |
| `02_rede.py` | A rede neural completa de um carro | `python3 02_rede.py` |
| `03_evolucao.py` | A simulação com 100 carros evoluindo | `.venv/bin/python 03_evolucao.py` |

Os dois primeiros só usam a biblioteca padrão do Python. Só o terceiro precisa do `pygame`.

### Controles da simulação

| Tecla | Ação |
|---|---|
| `ESPAÇO` | Liga ou desliga o modo turbo |
| `ESC` | Sai |

### Opções do `03_evolucao.py`

| Opção | Efeito |
|---|---|
| `--geracoes N` | Para depois de N gerações |
| `--pista NOME` | Treina em outra pista: `treino` (padrão), `suave`, `muitas_curvas`, `estreita` ou `dificil` |
| `--sem-janela` | Treina sem desenhar, bem mais rápido |

Exemplo: `.venv/bin/python 03_evolucao.py --sem-janela --geracoes 20`

### O que a simulação grava

Na pasta `resultados/`, criada ao rodar:

| Arquivo | Conteúdo |
|---|---|
| `campeao.json` | Os pesos do melhor carro até o momento |
| `historico.csv` | Melhor voltas e média de voltas, geração a geração |
| `curva_aprendizado.png` | O gráfico do aprendizado, salvo ao sair |

## Estrutura

```
01_neuronio.py   o neurônio
02_rede.py       a rede neural
03_evolucao.py   a simulação e a evolução
carro.py         o carro: sensores, cérebro e movimento
pista.py         as pistas
genoma_io.py     salvar e carregar o campeão
grafico.py       o gráfico de aprendizado
TEORIA.md        a explicação teórica
```

## Licença

[MIT](LICENSE)
