from __future__ import annotations

import streamlit as st

from src.db import SessionLocal
from src.init_db import init_db


@st.cache_resource
def init_database() -> None:
    init_db()


def get_session():
    init_database()
    return SessionLocal()
