from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models import Asset, Dividend, Transaction


def _parse_date(value: str | datetime) -> datetime.date:
    if isinstance(value, datetime):
        return value.date()
    return pd.to_datetime(value, dayfirst=True).date()


def get_or_create_asset(session: Session, nome: str, categoria: str | None, tipo: str | None, setor: str | None) -> Asset:
    asset = session.query(Asset).filter_by(nome=nome).one_or_none()
    if asset:
        if categoria and not asset.categoria:
            asset.categoria = categoria
        if tipo and not asset.tipo:
            asset.tipo = tipo
        if setor and not asset.setor:
            asset.setor = setor
        return asset

    asset = Asset(nome=nome, categoria=categoria, tipo=tipo, setor=setor)
    session.add(asset)
    session.flush()
    return asset


def import_excel(path: Path, session: Session) -> dict[str, int]:
    xls = pd.ExcelFile(path)
    imported = {"assets": 0, "transactions": 0, "dividends": 0}

    if "Ativos" in xls.sheet_names:
        ativos = pd.read_excel(xls, "Ativos")
        for _, row in ativos.iterrows():
            nome = str(row.get("Nome")).strip()
            if not nome or nome == "nan":
                continue
            asset = session.query(Asset).filter_by(nome=nome).one_or_none()
            if asset:
                updated = False
                for field, column in [("categoria", "Categoria"), ("tipo", "Tipo"), ("setor", "Setor")]:
                    value = row.get(column)
                    if value and getattr(asset, field) != value:
                        setattr(asset, field, value)
                        updated = True
                if updated:
                    session.add(asset)
                continue
            session.add(
                Asset(
                    nome=nome,
                    categoria=row.get("Categoria"),
                    tipo=row.get("Tipo"),
                    setor=row.get("Setor"),
                )
            )
            imported["assets"] += 1

    def handle_transactions(sheet: str, tipo_tx: str) -> None:
        if sheet not in xls.sheet_names:
            return
        df = pd.read_excel(xls, sheet)
        for _, row in df.iterrows():
            nome = str(row.get("Nome")).strip()
            if not nome or nome == "nan":
                continue
            asset = get_or_create_asset(session, nome, row.get("Categoria"), None, None)
            preco_unit = float(row.get("Valor un", 0) or 0)
            quantidade = float(row.get("Quantidade", 0) or 0)
            taxas = float(row.get("Taxas", 0) or 0)
            valor_total = row.get("Custo Total")
            if pd.isna(valor_total):
                valor_total = preco_unit * quantidade
            tx = Transaction(
                asset_id=asset.id,
                data=_parse_date(row.get("Data")),
                tipo=tipo_tx,
                preco_unit=preco_unit,
                quantidade=quantidade,
                taxas=taxas,
                valor_total=float(valor_total or 0),
                resultado=float(row.get("Resultado", 0) or 0) if tipo_tx == "SELL" else None,
                ganhos=float(row.get("Ganhos", 0) or 0) if tipo_tx == "SELL" else None,
            )
            session.add(tx)
            try:
                session.flush()
                imported["transactions"] += 1
            except IntegrityError:
                session.rollback()
                session.begin()

    handle_transactions("Entradas", "BUY")
    handle_transactions("Saidas", "SELL")

    if "Dividendos" in xls.sheet_names:
        df = pd.read_excel(xls, "Dividendos")
        for _, row in df.iterrows():
            nome = str(row.get("Nome")).strip()
            if not nome or nome == "nan":
                continue
            asset = get_or_create_asset(session, nome, row.get("Categoria"), None, None)
            dividend = Dividend(
                asset_id=asset.id,
                data=_parse_date(row.get("Data")),
                valor=float(row.get("Valor", 0) or 0),
            )
            session.add(dividend)
            try:
                session.flush()
                imported["dividends"] += 1
            except IntegrityError:
                session.rollback()
                session.begin()

    session.commit()
    return imported
