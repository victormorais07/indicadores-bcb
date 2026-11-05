import re
from pathlib import Path

from coletor.series import SERIES

ARQUIVO = Path(__file__).resolve().parent.parent / "README.md"

INICIO = "<!-- inicio-indicadores -->"
FIM = "<!-- fim-indicadores -->"


def formatar_numero(valor, casas):
    # 5.1234 -> 5,1234 (padrão brasileiro)
    return f"{valor:.{casas}f}".replace(".", ",")


def montar_tabela(dados):
    linhas = [
        "| Indicador | Último valor | Data |",
        "|---|---|---|",
    ]
    for nome, df in dados.items():
        if df.empty:
            continue
        ultimo = df.iloc[-1]
        serie = SERIES[nome]
        casas = 4 if nome == "dolar" else 2

        if nome == "ipca":
            data = ultimo["data"].strftime("%m/%Y")
        else:
            data = ultimo["data"].strftime("%d/%m/%Y")

        valor = formatar_numero(ultimo["valor"], casas)
        if serie["unidade"] == "R$":
            valor = f"R$ {valor}"
        else:
            valor = f"{valor} {serie['unidade']}"

        linhas.append(f"| {serie['nome']} | {valor} | {data} |")

    return "\n".join(linhas)


def atualizar(dados):
    """Troca o que estiver entre os marcadores do README pela tabela nova."""
    texto = ARQUIVO.read_text(encoding="utf-8")
    tabela = montar_tabela(dados)

    padrao = re.compile(re.escape(INICIO) + ".*?" + re.escape(FIM), re.DOTALL)
    if not padrao.search(texto):
        print("  marcadores não encontrados no README, pulando")
        return

    novo = padrao.sub(lambda _: f"{INICIO}\n{tabela}\n{FIM}", texto)
    ARQUIVO.write_text(novo, encoding="utf-8")
