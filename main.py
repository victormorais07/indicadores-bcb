"""Coleta os indicadores do Banco Central, salva em CSV e atualiza o gráfico e o README.

Uso: python main.py
"""
from datetime import date, timedelta

from coletor import armazenar, grafico, readme
from coletor.api_bcb import MAX_DIAS_POR_CONSULTA, buscar_serie
from coletor.series import INICIO_PADRAO, SERIES
from coletor.transformar import juntar, limpar

# volta alguns dias além do último salvo, caso o BC tenha corrigido algum valor recente
DIAS_DE_FOLGA = 7


def periodos(inicio, fim):
    """Quebra o intervalo em pedaços que a API aceita."""
    while inicio <= fim:
        fim_pedaco = min(inicio + timedelta(days=MAX_DIAS_POR_CONSULTA - 1), fim)
        yield inicio, fim_pedaco
        inicio = fim_pedaco + timedelta(days=1)


def atualizar_serie(nome, codigo):
    antigo = armazenar.carregar(nome)

    if antigo.empty:
        inicio = INICIO_PADRAO
    else:
        inicio = antigo["data"].max().date() - timedelta(days=DIAS_DE_FOLGA)

    hoje = date.today()
    registros = []
    for de, ate in periodos(inicio, hoje):
        registros += buscar_serie(codigo, de, ate)

    novo = limpar(registros)
    df = juntar(antigo, novo)
    armazenar.salvar(nome, df)

    adicionadas = len(df) - len(antigo)
    print(f"  {nome}: {len(df)} linhas ({adicionadas:+d})")
    return df


def main():
    print("Coletando dados do Banco Central...")
    dados = {}
    for nome, serie in SERIES.items():
        dados[nome] = atualizar_serie(nome, serie["codigo"])

    print("Gerando gráfico...")
    grafico.gerar(dados)

    print("Atualizando README...")
    readme.atualizar(dados)

    print("Pronto.")


if __name__ == "__main__":
    main()
