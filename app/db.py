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
    migrar()


# Colunas acrescentadas depois da v0.1.0. O create_all não altera tabelas que já existem,
# então bancos criados na versão anterior recebem as colunas novas aqui (SQLite e PostgreSQL).
COLUNAS_NOVAS = {
    "estudante": {"nome_responsavel": "VARCHAR(120)",
                  "consentimento_registrado_por": "INTEGER"},
    "trecho_material": {"embedding": "BLOB", "embedding_modelo": "VARCHAR(120)"},
    "material": {"origem": "VARCHAR(160)"},
}


def migrar():
    from sqlalchemy import inspect, text
    insp = inspect(engine)
    tipos_pg = {"BLOB": "BYTEA"}
    with engine.begin() as con:
        for tabela, colunas in COLUNAS_NOVAS.items():
            if not insp.has_table(tabela):
                continue
            existentes = {c["name"] for c in insp.get_columns(tabela)}
            for nome, tipo in colunas.items():
                if nome not in existentes:
                    if engine.dialect.name == "postgresql":
                        tipo = tipos_pg.get(tipo, tipo)
                    con.execute(text(f"ALTER TABLE {tabela} ADD COLUMN {nome} {tipo}"))
