from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sem janela, só gera o arquivo (precisa disso no GitHub Actions)
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from coletor.series import SERIES

ARQUIVO = Path(__file__).resolve().parent.parent / "imagens" / "indicadores.png"

CORES = {"dolar": "#2e7d32", "selic": "#1565c0", "ipca": "#c62828"}


def gerar(dados):
    """dados = {"dolar": DataFrame, "selic": DataFrame, ...}"""
    fig, eixos = plt.subplots(len(dados), 1, figsize=(10, 9), sharex=True)

    for eixo, (nome, df) in zip(eixos, dados.items()):
        serie = SERIES[nome]
        cor = CORES.get(nome, "#555555")

        if nome == "ipca":
            # IPCA é mensal, barra fica mais fácil de ler que linha
            eixo.bar(df["data"], df["valor"], width=20, color=cor)
            eixo.axhline(0, color="#999999", linewidth=0.8)
        else:
            eixo.plot(df["data"], df["valor"], color=cor, linewidth=1.5)

        eixo.set_title(f"{serie['nome']} ({serie['unidade']})", loc="left", fontsize=11)
        eixo.grid(alpha=0.3)
        eixo.spines[["top", "right"]].set_visible(False)

    eixos[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.suptitle("Indicadores do Banco Central", fontsize=14, fontweight="bold")
    fig.tight_layout()

    ARQUIVO.parent.mkdir(exist_ok=True)
    fig.savefig(ARQUIVO, dpi=110)
    plt.close(fig)
