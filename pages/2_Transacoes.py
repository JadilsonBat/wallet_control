from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.importer import import_excel
from src.models import Asset, Transaction
from src.ui_helpers import get_session


st.set_page_config(page_title="Transações", layout="wide")
st.title("Transações")

with get_session() as session:
    assets = session.query(Asset).order_by(Asset.nome).all()
    transactions = (
        session.query(Transaction)
        .join(Asset, Transaction.asset_id == Asset.id)
        .order_by(Transaction.data.desc())
        .all()
    )
    transaction_rows = [
        {
            "Data": tx.data,
            "Ativo": tx.asset.nome,
            "Tipo": tx.tipo,
            "Preço": tx.preco_unit,
            "Quantidade": tx.quantidade,
            "Taxas": tx.taxas,
            "Valor total": tx.valor_total,
            "Resultado": tx.resultado,
            "Ganhos": tx.ganhos,
        }
        for tx in transactions
    ]

st.subheader("Importar Excel")
uploaded_file = st.file_uploader("Selecione Investimentos.xlsx", type=["xlsx"])
if uploaded_file:
    temp_path = Path("data") / uploaded_file.name
    temp_path.write_bytes(uploaded_file.getbuffer())
    with get_session() as session:
        result = import_excel(temp_path, session)
    st.success(f"Importação concluída: {result}")

st.subheader("Adicionar transação")
with st.form("add_transaction"):
    asset_nome = st.selectbox("Ativo", options=[a.nome for a in assets] + ["NOVO ATIVO"])
    new_asset_nome = st.text_input("Nome do novo ativo", disabled=asset_nome != "NOVO ATIVO")
    categoria = st.text_input("Categoria", disabled=asset_nome != "NOVO ATIVO")
    tipo = st.text_input("Tipo", disabled=asset_nome != "NOVO ATIVO")
    setor = st.text_input("Setor", disabled=asset_nome != "NOVO ATIVO")
    data = st.date_input("Data")
    tipo_tx = st.selectbox("Tipo", ["BUY", "SELL"])
    preco = st.number_input("Preço unitário", min_value=0.0, step=0.01)
    quantidade = st.number_input("Quantidade", min_value=0.0, step=0.01)
    taxas = st.number_input("Taxas", min_value=0.0, step=0.01)
    valor_total = st.number_input("Valor total", min_value=0.0, step=0.01)
    resultado = st.number_input("Resultado (apenas SELL)", min_value=0.0, step=0.01)
    ganhos = st.number_input("Ganhos (apenas SELL)", min_value=0.0, step=0.01)
    submitted = st.form_submit_button("Salvar")

    if submitted:
        with get_session() as session:
            if asset_nome == "NOVO ATIVO":
                asset = Asset(
                    nome=new_asset_nome,
                    categoria=categoria or None,
                    tipo=tipo or None,
                    setor=setor or None,
                )
                session.add(asset)
                session.flush()
            else:
                asset = session.query(Asset).filter_by(nome=asset_nome).one()
            tx = Transaction(
                asset_id=asset.id,
                data=data,
                tipo=tipo_tx,
                preco_unit=preco,
                quantidade=quantidade,
                taxas=taxas,
                valor_total=valor_total,
                resultado=resultado if tipo_tx == "SELL" else None,
                ganhos=ganhos if tipo_tx == "SELL" else None,
            )
            session.add(tx)
            session.commit()
        st.success("Transação adicionada.")

st.subheader("Lista de transações")
if transaction_rows:
    df = pd.DataFrame(transaction_rows)
    st.dataframe(df, use_container_width=True)
    st.download_button("Exportar CSV", data=df.to_csv(index=False), file_name="transacoes.csv")
else:
    st.info("Nenhuma transação encontrada.")
