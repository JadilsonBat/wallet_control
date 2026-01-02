from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

from src.logging_config import setup_logging

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

setup_logging()
st.set_page_config(page_title="Controle de Investimentos", layout="wide")

st.title("Controle de Investimentos")
st.markdown(
    """
Bem-vindo! Use o menu lateral para navegar entre as páginas:

- **Visão Geral**: resumo da carteira e curva de patrimônio.
- **Transações**: importação da planilha e gestão de compras/vendas.
- **Proventos**: cadastro e lista de dividendos.
- **Ativos (Carteira)**: posições atuais e atualização de preços.
- **Comparação CDI**: performance da carteira versus CDI.
- **Dashboard (Alocação)**: gráficos de distribuição.
"""
)
