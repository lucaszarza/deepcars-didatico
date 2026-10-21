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
| `04_teste_em_outra_pista.py` | O campeão em pistas que ele nunca viu | `.venv/bin/python 04_teste_em_outra_pista.py` |

Os dois primeiros só usam a biblioteca padrão do Python. Os outros precisam do `pygame`.

O passo 4 usa o campeão gravado por você em `resultados/campeao.json` e, se ele não existir, o `exemplos/campeao_exemplo.json`, que já vem no repositório. Dá para testar o passo 4 sem treinar antes.

### Controles das janelas

| Tecla | Ação | Janela |
|---|---|---|
| `ESPAÇO` | Liga ou desliga o modo turbo | passos 3 e 4 |
| `TAB` | Troca a pista que aparece (treino em várias pistas) | passo 3 |
| `1` a `5` | Troca de pista | passo 4 |
| `R` | Recomeça a corrida | passo 4 |
| `ESC` | Sai | passos 3 e 4 |

### Opções do `03_evolucao.py`

| Opção | Efeito |
|---|---|
| `--geracoes N` | Para depois de N gerações |
| `--pistas A,B,C` | Pistas de treino, separadas por vírgula: `treino` (padrão), `suave`, `muitas_curvas`, `estreita`, `dificil`. Com mais de uma, cada cérebro corre em todas e a nota é a média |
| `--sem-janela` | Treina sem desenhar, bem mais rápido |
| `--turbo` | Abre a janela já em modo turbo |

Exemplos:

```bash
.venv/bin/python 03_evolucao.py --sem-janela --geracoes 20
.venv/bin/python 03_evolucao.py --pistas treino,suave,muitas_curvas   # treino em 3 pistas
```

### Opções do `04_teste_em_outra_pista.py`

| Opção | Efeito |
|---|---|
| `ARQUIVO.json` | Usa outro campeão, em vez do padrão |
| `--relatorio` | Mostra uma tabela no terminal, sem abrir janela |
| `--pista NOME` | Pista em que a janela começa |

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
04_teste_em_outra_pista.py   o campeão em outras pistas
carro.py         o carro: sensores, cérebro e movimento
sprite.py        o desenho do carrinho
pista.py         as pistas
genoma_io.py     salvar e carregar o campeão
grafico.py       o gráfico de aprendizado
exemplos/        dois campeões prontos (uma pista e três pistas) e a curva de um treino
TEORIA.md        a explicação teórica
```

## Licença

[MIT](LICENSE)
