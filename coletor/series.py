# Séries do SGS (Sistema Gerenciador de Séries Temporais) do Banco Central.
# Os códigos dá pra procurar em https://www3.bcb.gov.br/sgspub
from datetime import date

INICIO_PADRAO = date(2020, 1, 1)

SERIES = {
    "dolar": {
        "codigo": 1,
        "nome": "Dólar comercial (venda)",
        "unidade": "R$",
    },
    "selic": {
        "codigo": 432,
        "nome": "Meta Selic",
        "unidade": "% a.a.",
    },
    "ipca": {
        "codigo": 433,
        "nome": "IPCA mensal",
        "unidade": "% no mês",
    },
}
