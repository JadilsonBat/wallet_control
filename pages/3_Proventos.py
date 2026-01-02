from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.models import Asset, Dividend
from src.ui_helpers import get_session


st.set_page_config(page_title="Proventos", layout="wide")
st.title("Proventos")

with get_session() as session:
    assets = session.query(Asset).order_by(Asset.nome).all()
    dividends = (
        session.query(Dividend)
        .join(Asset, Dividend.asset_id == Asset.id)
        .order_by(Dividend.data.desc())
        .all()
    )
    dividend_rows = [{"Data": div.data, "Ativo": div.asset.nome, "Valor": div.valor} for div in dividends]

st.subheader("Adicionar provento")
with st.form("add_dividend"):
    asset_nome = st.selectbox("Ativo", options=[a.nome for a in assets])
    data = st.date_input("Data")
    valor = st.number_input("Valor", min_value=0.0, step=0.01)
    submitted = st.form_submit_button("Salvar")
    if submitted:
        with get_session() as session:
            asset = session.query(Asset).filter_by(nome=asset_nome).one()
            session.add(Dividend(asset_id=asset.id, data=data, valor=valor))
            session.commit()
        st.success("Provento adicionado.")

st.subheader("Lista de proventos")
if dividend_rows:
    df = pd.DataFrame(dividend_rows)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nenhum provento encontrado.")
