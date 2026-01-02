from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    categoria: Mapped[str | None] = mapped_column(String, nullable=True)
    tipo: Mapped[str | None] = mapped_column(String, nullable=True)
    setor: Mapped[str | None] = mapped_column(String, nullable=True)
    ticker_mercado: Mapped[str | None] = mapped_column(String, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(String, nullable=True)

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="asset", cascade="all, delete-orphan")
    dividends: Mapped[list["Dividend"]] = relationship(back_populates="asset", cascade="all, delete-orphan")
    prices: Mapped[list["Price"]] = relationship(back_populates="asset", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint(
            "asset_id",
            "data",
            "tipo",
            "preco_unit",
            "quantidade",
            "taxas",
            "valor_total",
            "resultado",
            "ganhos",
            name="uq_transactions_natural",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    tipo: Mapped[str] = mapped_column(String, nullable=False)
    preco_unit: Mapped[float] = mapped_column(Float, nullable=False)
    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    taxas: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    valor_total: Mapped[float] = mapped_column(Float, nullable=False)
    resultado: Mapped[float | None] = mapped_column(Float, nullable=True)
    ganhos: Mapped[float | None] = mapped_column(Float, nullable=True)

    asset: Mapped["Asset"] = relationship(back_populates="transactions")


class Dividend(Base):
    __tablename__ = "dividends"
    __table_args__ = (UniqueConstraint("asset_id", "data", "valor", name="uq_dividends_natural"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)

    asset: Mapped["Asset"] = relationship(back_populates="dividends")


class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (UniqueConstraint("asset_id", "data", "fonte", name="uq_prices_natural"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    preco: Mapped[float] = mapped_column(Float, nullable=False)
    fonte: Mapped[str] = mapped_column(String, nullable=False, default="manual")

    asset: Mapped["Asset"] = relationship(back_populates="prices")
