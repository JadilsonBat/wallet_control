from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models import Asset, Dividend, Price, Transaction


def list_assets(session: Session) -> list[Asset]:
    return session.query(Asset).order_by(Asset.nome).all()


def list_transactions(session: Session) -> list[Transaction]:
    return session.query(Transaction).order_by(Transaction.data).all()


def list_dividends(session: Session) -> list[Dividend]:
    return session.query(Dividend).order_by(Dividend.data).all()


def latest_prices(session: Session) -> dict[int, float]:
    sub = (
        session.query(Price.asset_id, func.max(Price.data).label("max_date"))
        .group_by(Price.asset_id)
        .subquery()
    )
    rows = (
        session.query(Price.asset_id, Price.preco)
        .join(sub, (Price.asset_id == sub.c.asset_id) & (Price.data == sub.c.max_date))
        .all()
    )
    return {asset_id: preco for asset_id, preco in rows}
