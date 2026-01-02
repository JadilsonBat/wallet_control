from datetime import date

import pandas as pd

from src.models import Transaction
from src.services.cdi import cdi_accumulated_index
from src.services.portfolio import compute_positions, portfolio_timeseries


def test_compute_positions_price_average():
    txs = [
        Transaction(
            asset_id=1,
            data=date(2024, 1, 1),
            tipo="BUY",
            preco_unit=10.0,
            quantidade=10.0,
            taxas=1.0,
            valor_total=101.0,
        ),
        Transaction(
            asset_id=1,
            data=date(2024, 2, 1),
            tipo="BUY",
            preco_unit=20.0,
            quantidade=5.0,
            taxas=0.0,
            valor_total=100.0,
        ),
        Transaction(
            asset_id=1,
            data=date(2024, 3, 1),
            tipo="SELL",
            preco_unit=30.0,
            quantidade=5.0,
            taxas=0.0,
            valor_total=150.0,
        ),
    ]

    positions = compute_positions(txs)
    position = positions[1]
    assert position.quantidade == 10.0
    assert round(position.preco_medio, 2) == 15.1


def test_portfolio_timeseries():
    txs = [
        Transaction(
            asset_id=1,
            data=date(2024, 1, 1),
            tipo="BUY",
            preco_unit=10.0,
            quantidade=10.0,
            taxas=0.0,
            valor_total=100.0,
        ),
        Transaction(
            asset_id=1,
            data=date(2024, 1, 10),
            tipo="BUY",
            preco_unit=12.0,
            quantidade=5.0,
            taxas=0.0,
            valor_total=60.0,
        ),
    ]
    df = portfolio_timeseries(txs)
    assert df.iloc[-1]["patrimonio"] == 15 * 12.0


def test_cdi_accumulated_index():
    cdi = pd.DataFrame(
        {
            "data": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "cdi_diario": [0.1, 0.2],
        }
    )
    idx = cdi_accumulated_index(cdi)
    assert round(idx["indice"].iloc[-1], 4) == round(100 * 1.001 * 1.002, 4)
