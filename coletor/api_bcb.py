import time

import requests

URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"

# a API limita consultas de séries diárias a 10 anos por vez
MAX_DIAS_POR_CONSULTA = 365 * 10


def buscar_serie(codigo, inicio, fim, tentativas=3):
    """Busca os valores de uma série entre duas datas.

    Retorna a lista crua que a API devolve: [{"data": "dd/mm/aaaa", "valor": "1.23"}, ...]
    """
    params = {
        "formato": "json",
        "dataInicial": inicio.strftime("%d/%m/%Y"),
        "dataFinal": fim.strftime("%d/%m/%Y"),
    }

    for tentativa in range(1, tentativas + 1):
        try:
            resp = requests.get(URL.format(codigo=codigo), params=params, timeout=30)

            # quando não tem nada no período (feriado, fim de semana) a API responde 404
            if resp.status_code == 404:
                return []

            resp.raise_for_status()
            return resp.json()

        except requests.RequestException as erro:
            if tentativa == tentativas:
                raise
            espera = 5 * tentativa
            print(f"  erro na série {codigo} ({erro}), tentando de novo em {espera}s...")
            time.sleep(espera)
