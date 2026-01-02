from __future__ import annotations

import argparse
from pathlib import Path

from src.db import SessionLocal
from src.importer import import_excel
from src.init_db import init_db
from src.logging_config import setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Importa a planilha Investimentos.xlsx para o SQLite.")
    parser.add_argument("arquivo", type=Path, help="Caminho para Investimentos.xlsx")
    args = parser.parse_args()

    setup_logging()
    init_db()
    with SessionLocal() as session:
        result = import_excel(args.arquivo, session)
    print(f"Importação concluída: {result}")


if __name__ == "__main__":
    main()
