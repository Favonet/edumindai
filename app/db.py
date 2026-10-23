"""Conexão com o banco de dados.

Em desenvolvimento usa SQLite (arquivo edumindai.db). Em homologação/produção basta
definir a variável DATABASE_URL apontando para o PostgreSQL, ex.:
    postgresql+psycopg://usuario:senha@host:5432/edumindai
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./edumindai.db")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def criar_tabelas():
    from . import models  # noqa: F401  (registra os modelos)
    Base.metadata.create_all(bind=engine)
