from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.models import Asset, Dividend, Transaction
from src.queries import latest_prices
from src.services.portfolio import compute_positions, portfolio_timeseries
from src.ui_helpers import get_session


st.set_page_config(page_title="Visão Geral", layout="wide")
st.title("Visão Geral")

with get_session() as session:
    assets = session.query(Asset).all()
    transactions = session.query(Transaction).all()
    dividends = session.query(Dividend).all()
    prices = latest_prices(session)

if not assets:
    st.info("Nenhum dado encontrado. Importe a planilha na página de Transações.")
    st.stop()

positions = compute_positions(transactions)

investido_total = sum(
    tx.valor_total if tx.tipo.upper() == "BUY" else -tx.valor_total for tx in transactions
)
dividendos_total = sum(div.valor for div in dividends)
ganhos_vendas = sum(tx.ganhos or 0 for tx in transactions if tx.tipo.upper() == "SELL")
taxas_pagadas = sum(tx.taxas for tx in transactions)

valor_atual = 0.0
rows = []
for asset in assets:
    position = positions.get(asset.id)
    if not position:
        continue
    price = prices.get(asset.id)
    if price is None:
        last_tx = max(
            (tx for tx in transactions if tx.asset_id == asset.id), key=lambda t: t.data, default=None
        )
        price = last_tx.preco_unit if last_tx else 0.0
    valor_atual += position.quantidade * price
    rows.append(
        {
            "Categoria": asset.categoria or "Sem categoria",
            "Nome": asset.nome,
            "Valor": position.quantidade * price,
        }
    )

rentabilidade_total = (
    (valor_atual + dividendos_total + ganhos_vendas - investido_total) / investido_total
    if investido_total
    else 0.0
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Investido total", f"R$ {investido_total:,.2f}")
col2.metric("Valor atual", f"R$ {valor_atual:,.2f}")
col3.metric("Dividendos acumulados", f"R$ {dividendos_total:,.2f}")
col4.metric("Ganhos com vendas", f"R$ {ganhos_vendas:,.2f}")

col5, col6 = st.columns(2)
col5.metric("Rentabilidade total", f"{rentabilidade_total:.2%}")
col6.metric("Taxas pagas", f"R$ {taxas_pagadas:,.2f}")

st.subheader("Curva do patrimônio (baseada em preços de transações)")
timeseries = portfolio_timeseries(transactions)
if not timeseries.empty:
    fig = px.line(timeseries, x="data", y="patrimonio", labels={"patrimonio": "Patrimônio"})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Sem dados suficientes para curva do patrimônio.")

st.subheader("Resumo por categoria")
df = pd.DataFrame(rows)
if not df.empty:
    summary = df.groupby("Categoria", as_index=False)["Valor"].sum()
    summary["Participação"] = summary["Valor"] / summary["Valor"].sum()
    st.dataframe(summary, use_container_width=True)
else:
    st.info("Sem posições atuais para exibir.")
