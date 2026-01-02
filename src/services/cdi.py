from __future__ import annotations

from datetime import date

import pandas as pd
import requests

BCB_ENDPOINT = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados"


def fetch_cdi_series(start_date: date, end_date: date) -> pd.DataFrame:
    params = {
        "formato": "json",
        "dataInicial": start_date.strftime("%d/%m/%Y"),
        "dataFinal": end_date.strftime("%d/%m/%Y"),
    }
    response = requests.get(BCB_ENDPOINT, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)
    df["data"] = pd.to_datetime(df["data"], dayfirst=True)
    df["valor"] = df["valor"].astype(float)
    return df.rename(columns={"valor": "cdi_diario"})


def cdi_accumulated_index(cdi_df: pd.DataFrame) -> pd.DataFrame:
    df = cdi_df.copy()
    df["fator"] = 1 + df["cdi_diario"] / 100.0
    df["indice"] = df["fator"].cumprod() * 100.0
    return df[["data", "indice"]]
