from pathlib import Path

import pandas as pd

from coletor.transformar import COLUNAS

PASTA_DADOS = Path(__file__).resolve().parent.parent / "dados"


def caminho(nome):
    return PASTA_DADOS / f"{nome}.csv"


def carregar(nome):
    arquivo = caminho(nome)
    if not arquivo.exists():
        return pd.DataFrame(columns=COLUNAS)
    return pd.read_csv(arquivo, parse_dates=["data"])


def salvar(nome, df):
    PASTA_DADOS.mkdir(exist_ok=True)
    arquivo = caminho(nome)

    # grava num temporário e depois troca, pra não deixar o csv pela metade se der erro
    temporario = arquivo.with_suffix(".tmp")
    # \n fixo pra o arquivo sair igual no Windows e no Linux do GitHub Actions
    df.to_csv(temporario, index=False, date_format="%Y-%m-%d", lineterminator="\n")
    temporario.replace(arquivo)
