import pandas as pd

COLUNAS = ["data", "valor"]


def limpar(registros):
    """Transforma o JSON da API num DataFrame com data de verdade e valor numérico."""
    if not registros:
        return pd.DataFrame(columns=COLUNAS)

    df = pd.DataFrame(registros)
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    # linha com data ou valor quebrado não serve pra nada
    df = df.dropna(subset=COLUNAS)
    return df[COLUNAS]


def juntar(antigo, novo):
    """Junta o que já estava salvo com o que veio agora.

    Se a mesma data aparecer nos dois, fica o valor novo (o BC às vezes corrige dados).
    """
    df = pd.concat([antigo, novo], ignore_index=True)
    # se um dos lados vier vazio o pandas perde o tipo da coluna, então garante aqui
    df["data"] = pd.to_datetime(df["data"])
    df = df.drop_duplicates(subset="data", keep="last")
    return df.sort_values("data").reset_index(drop=True)
