"""
EXPERIMENTO A - Salvar e carregar os vencedores.

O "conhecimento" de um carro é só a lista de pesos da rede (o genoma).
Por isso um campeão cabe num arquivo JSON de poucas linhas:

    {
      "n_pesos": 62,
      "info": {"geracao": 12, "voltas": 4.9, "pista": "treino"},
      "genoma": [0.31, -1.2, ...]
    }

Abra um arquivo desses num editor de texto: é literalmente isso que o carro sabe.
"""
import json
import os

from carro import rede


def salvar_campeao(caminho, genoma, **info):
    os.makedirs(os.path.dirname(os.path.abspath(caminho)), exist_ok=True)
    dados = {"n_pesos": len(genoma), "info": info, "genoma": list(genoma)}
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=2, ensure_ascii=False)


def carregar_campeao(caminho):
    """Devolve (genoma, info). Dá erro claro se o arquivo não combina com a rede atual."""
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    genoma = dados.get("genoma")
    if not isinstance(genoma, list) or not all(isinstance(p, (int, float)) for p in genoma):
        raise ValueError(f"{caminho}: o campo 'genoma' deve ser uma lista de números")
    if not rede.genoma_valido(genoma):
        raise ValueError(
            f"{caminho}: tem {len(genoma)} pesos, mas a rede atual precisa de {rede.N_PESOS} "
            f"(ou {rede.N_PESOS_SO_VOLANTE}, da rede antiga sem acelerador). "
            "O campeão foi treinado com outro número de sensores ou neurônios."
        )
    return [float(p) for p in genoma], dados.get("info", {})
