from __future__ import annotations

from src.db import engine
from src.models import Base


def init_db() -> None:
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
