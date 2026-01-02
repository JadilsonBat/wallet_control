from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.models import Transaction
from src.services.cdi import cdi_accumulated_index, fetch_cdi_series
from src.services.portfolio import portfolio_timeseries
from src.ui_helpers import get_session


st.set_page_config(page_title="Comparação CDI", layout="wide")
st.title("Comparação com CDI")

with get_session() as session:
    transactions = session.query(Transaction).all()

if not transactions:
    st.info("Importe transações para comparar com CDI.")
    st.stop()

ts = portfolio_timeseries(transactions)
if ts.empty:
    st.info("Sem dados suficientes para curva de patrimônio.")
    st.stop()

start_date = st.date_input("Data inicial", value=ts["data"].min())
end_date = st.date_input("Data final", value=ts["data"].max())

filtered = ts[(ts["data"] >= pd.to_datetime(start_date)) & (ts["data"] <= pd.to_datetime(end_date))]
filtered = filtered.sort_values("data")
filtered["indice_carteira"] = filtered["patrimonio"] / filtered["patrimonio"].iloc[0] * 100

try:
    cdi_df = fetch_cdi_series(start_date, end_date)
    cdi_index = cdi_accumulated_index(cdi_df)
except Exception as exc:  # noqa: BLE001
    st.warning(f"Não foi possível obter CDI automaticamente: {exc}")
    cdi_index = pd.DataFrame(columns=["data", "indice"])

if not cdi_index.empty:
    merged = pd.merge(
        filtered[["data", "indice_carteira"]],
        cdi_index,
        on="data",
        how="left",
    ).sort_values("data")
    merged["indice"] = merged["indice"].ffill()
    fig = px.line(
        merged,
        x="data",
        y=["indice_carteira", "indice"],
        labels={"value": "Índice (base 100)", "variable": "Série"},
    )
    st.plotly_chart(fig, use_container_width=True)
    retorno_carteira = merged["indice_carteira"].iloc[-1] / merged["indice_carteira"].iloc[0] - 1
    retorno_cdi = merged["indice"].iloc[-1] / merged["indice"].iloc[0] - 1
    st.metric("Retorno carteira", f"{retorno_carteira:.2%}")
    st.metric("Retorno CDI", f"{retorno_cdi:.2%}")
else:
    st.info("CDI indisponível. Verifique a conexão com o Banco Central.")
