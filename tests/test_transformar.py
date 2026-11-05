from datetime import date

import pandas as pd

from coletor.transformar import juntar, limpar
from main import periodos


def test_limpar_converte_data_e_valor():
    df = limpar([{"data": "03/11/2026", "valor": "5.1234"}])

    assert df["data"].iloc[0] == pd.Timestamp("2026-11-03")
    assert df["valor"].iloc[0] == 5.1234


def test_limpar_descarta_linha_quebrada():
    df = limpar([
        {"data": "03/11/2026", "valor": "5.10"},
        {"data": "data errada", "valor": "5.20"},
        {"data": "04/11/2026", "valor": ""},
    ])

    assert len(df) == 1


def test_limpar_lista_vazia():
    df = limpar([])

    assert df.empty
    assert list(df.columns) == ["data", "valor"]


def test_juntar_fica_com_valor_novo_e_ordena():
    antigo = limpar([
        {"data": "03/11/2026", "valor": "5.00"},
        {"data": "01/11/2026", "valor": "4.90"},
    ])
    novo = limpar([
        {"data": "03/11/2026", "valor": "5.05"},  # corrigido pelo BC
        {"data": "04/11/2026", "valor": "5.10"},
    ])

    df = juntar(antigo, novo)

    assert list(df["valor"]) == [4.90, 5.05, 5.10]


def test_periodos_quebra_intervalo_grande():
    pedacos = list(periodos(date(2000, 1, 1), date(2026, 1, 1)))

    assert pedacos[0][0] == date(2000, 1, 1)
    assert pedacos[-1][1] == date(2026, 1, 1)
    assert len(pedacos) == 3
    # um pedaço começa no dia seguinte ao fim do anterior
    for (_, fim), (inicio, _) in zip(pedacos, pedacos[1:]):
        assert (inicio - fim).days == 1
