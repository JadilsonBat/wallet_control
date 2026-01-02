from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date

import pandas as pd

from src.models import Transaction


@dataclass
class PositionSnapshot:
    asset_id: int
    quantidade: float
    preco_medio: float
    investido_liquido: float


def compute_positions(transactions: list[Transaction]) -> dict[int, PositionSnapshot]:
    state: dict[int, dict[str, float]] = defaultdict(lambda: {"qty": 0.0, "cost": 0.0})

    for tx in sorted(transactions, key=lambda t: t.data):
        current = state[tx.asset_id]
        if tx.tipo.upper() == "BUY":
            total_cost = tx.preco_unit * tx.quantidade + tx.taxas
            current["qty"] += tx.quantidade
            current["cost"] += total_cost
        else:
            avg_price = current["cost"] / current["qty"] if current["qty"] else 0.0
            current["qty"] -= tx.quantidade
            current["cost"] -= avg_price * tx.quantidade

    positions: dict[int, PositionSnapshot] = {}
    for asset_id, values in state.items():
        qty = values["qty"]
        cost = values["cost"]
        avg_price = cost / qty if qty else 0.0
        positions[asset_id] = PositionSnapshot(
            asset_id=asset_id,
            quantidade=qty,
            preco_medio=avg_price,
            investido_liquido=cost,
        )
    return positions


def portfolio_timeseries(transactions: list[Transaction]) -> pd.DataFrame:
    if not transactions:
        return pd.DataFrame(columns=["data", "patrimonio"])

    data_points: dict[date, list[Transaction]] = defaultdict(list)
    for tx in transactions:
        data_points[tx.data].append(tx)

    dates = sorted(data_points.keys())
    qty_map: dict[int, float] = defaultdict(float)
    last_price: dict[int, float] = defaultdict(float)
    rows: list[dict[str, float | date]] = []

    for day in dates:
        for tx in data_points[day]:
            if tx.tipo.upper() == "BUY":
                qty_map[tx.asset_id] += tx.quantidade
            else:
                qty_map[tx.asset_id] -= tx.quantidade
            last_price[tx.asset_id] = tx.preco_unit

        patrimonio = sum(qty_map[asset_id] * last_price[asset_id] for asset_id in qty_map)
        rows.append({"data": day, "patrimonio": patrimonio})

    df = pd.DataFrame(rows).sort_values("data")
    return df
