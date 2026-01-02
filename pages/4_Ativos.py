from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.models import Asset, Dividend, Price, Transaction
from src.queries import latest_prices
from src.services.portfolio import compute_positions
from src.ui_helpers import get_session


st.set_page_config(page_title="Ativos (Carteira)", layout="wide")
st.title("Ativos (Carteira)")

with get_session() as session:
    assets = session.query(Asset).order_by(Asset.nome).all()
    transactions = session.query(Transaction).all()
    dividends = session.query(Dividend).all()
    prices = latest_prices(session)

positions = compute_positions(transactions)
dividend_map = {}
for div in dividends:
    dividend_map.setdefault(div.asset_id, 0.0)
    dividend_map[div.asset_id] += div.valor

st.subheader("Atualizar metadata e preço")
with st.form("update_asset"):
    asset_nome = st.selectbox("Ativo", options=[a.nome for a in assets])
    selected = next(a for a in assets if a.nome == asset_nome)
    categoria = st.text_input("Categoria", value=selected.categoria or "")
    tipo = st.text_input("Tipo", value=selected.tipo or "")
    setor = st.text_input("Setor", value=selected.setor or "")
    ticker = st.text_input("Ticker mercado", value=selected.ticker_mercado or "")
    observacoes = st.text_area("Observações", value=selected.observacoes or "")
    preco_atual = st.number_input("Preço atual", min_value=0.0, step=0.01)
    data_preco = st.date_input("Data do preço")
    submitted = st.form_submit_button("Salvar")
    if submitted:
        with get_session() as session:
            asset = session.query(Asset).filter_by(nome=asset_nome).one()
            asset.categoria = categoria or None
            asset.tipo = tipo or None
            asset.setor = setor or None
            asset.ticker_mercado = ticker or None
            asset.observacoes = observacoes or None
            if preco_atual > 0:
                session.add(Price(asset_id=asset.id, data=data_preco, preco=preco_atual, fonte="manual"))
            session.commit()
        st.success("Ativo atualizado.")

st.subheader("Posições atuais")
rows = []
for asset in assets:
    position = positions.get(asset.id)
    if not position or position.quantidade == 0:
        continue
    price = prices.get(asset.id, 0.0)
    valor_atual = position.quantidade * price
    rows.append(
        {
            "Ativo": asset.nome,
            "Categoria": asset.categoria,
            "Tipo": asset.tipo,
            "Setor": asset.setor,
            "Quantidade": position.quantidade,
            "Preço médio": position.preco_medio,
            "Investido líquido": position.investido_liquido,
            "Preço atual": price,
            "Valor atual": valor_atual,
            "Dividendos": dividend_map.get(asset.id, 0.0),
            "Participação": 0.0,
        }
    )

df = pd.DataFrame(rows)
if not df.empty:
    total = df["Valor atual"].sum()
    df["Participação"] = df["Valor atual"] / total
    st.dataframe(df, use_container_width=True)
else:
    st.info("Sem posições com quantidade positiva.")
