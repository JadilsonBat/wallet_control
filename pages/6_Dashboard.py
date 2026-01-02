from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.models import Asset, Transaction
from src.queries import latest_prices
from src.services.portfolio import compute_positions
from src.ui_helpers import get_session


st.set_page_config(page_title="Dashboard", layout="wide")
st.title("Dashboard de Alocação")

with get_session() as session:
    assets = session.query(Asset).all()
    transactions = session.query(Transaction).all()
    prices = latest_prices(session)

positions = compute_positions(transactions)
rows = []
for asset in assets:
    position = positions.get(asset.id)
    if not position or position.quantidade == 0:
        continue
    price = prices.get(asset.id, 0.0)
    valor = position.quantidade * price
    rows.append(
        {
            "Ativo": asset.nome,
            "Categoria": asset.categoria or "Sem categoria",
            "Tipo": asset.tipo or "Sem tipo",
            "Setor": asset.setor or "Sem setor",
            "Valor": valor,
        }
    )

df = pd.DataFrame(rows)
if df.empty:
    st.info("Sem dados para gerar o dashboard.")
    st.stop()

col1, col2 = st.columns(2)
fig_cat = px.pie(df, names="Categoria", values="Valor", title="Participação por categoria")
col1.plotly_chart(fig_cat, use_container_width=True)

fig_tipo = px.bar(
    df.groupby("Tipo", as_index=False)["Valor"].sum(),
    x="Tipo",
    y="Valor",
    title="Participação por tipo",
)
col2.plotly_chart(fig_tipo, use_container_width=True)

fig_setor = px.bar(
    df.groupby("Setor", as_index=False)["Valor"].sum(),
    x="Setor",
    y="Valor",
    title="Participação por setor",
)
st.plotly_chart(fig_setor, use_container_width=True)

top10 = df.sort_values("Valor", ascending=False).head(10)
fig_top = px.bar(top10, x="Ativo", y="Valor", title="Top 10 ativos por participação")
st.plotly_chart(fig_top, use_container_width=True)
