"""Testes das funcionalidades da release 0.2.0."""
import numpy as np
import pytest
from sqlalchemy import create_engine, inspect, text

from app import rag

TRECHOS = [(0, 1, "A clorofila é o pigmento verde das folhas."),
           (1, 1, "A precipitação acontece quando as gotículas caem como chuva."),
           (2, 2, "O numerador indica quantas partes foram consideradas.")]


class CodificadorFalso:
    """Vetores fixos: cada texto vira um vetor de 3 posições pelo assunto que menciona,
    simulando um modelo que entende paráfrases ("por que chove" ~ "precipitação")."""
    nome = "falso"
    ASSUNTOS = (("clorofila", "verde", "folha"), ("chuva", "chove", "precipita"),
                ("numerador", "parte", "pedaço"))

    def disponivel(self):
        return True

    def codificar(self, textos, tipo="passage"):
        saida = []
        for t in textos:
            v = np.array([float(any(p in t.lower() for p in ps)) for ps in self.ASSUNTOS]) + 0.01
            saida.append(v / np.linalg.norm(v))
        return np.array(saida, dtype=np.float32)


@pytest.fixture
def falso(monkeypatch):
    c = CodificadorFalso()
    monkeypatch.setattr(rag, "codificador", c)
    return c


def test_busca_hibrida_acha_parafrase_que_o_tfidf_nao_acha(falso):
    ind = rag.IndiceSemantico()
    ind.construir(TRECHOS, falso.codificar([t[2] for t in TRECHOS]))
    assert ind.modo.startswith("híbrida")
    # "por que chove" não tem nenhuma palavra em comum com o trecho de precipitação
    assert ind.buscar("por que chove", k=1, modo="tfidf") == []
    r = ind.buscar("por que chove", k=1)
    assert r and "precipitação" in r[0].texto


def test_sem_embeddings_o_indice_volta_para_tfidf():
    ind = rag.IndiceSemantico()
    ind.construir(TRECHOS, None)
    assert ind.modo == "TF-IDF"
    r = ind.buscar("o que é a clorofila", k=1)
    assert r and "clorofila" in r[0].texto


def test_codificador_indisponivel_nao_quebra_a_busca(monkeypatch):
    c = rag.CodificadorEmbeddings("modelo/que-nao-existe")
    monkeypatch.setenv("EDUMIND_EMBEDDINGS", "1")
    monkeypatch.setattr(rag, "codificador", c)
    import builtins
    original = builtins.__import__

    def sem_pacote(nome, *a, **k):
        if nome.startswith("sentence_transformers"):
            raise ImportError("pacote ausente")
        return original(nome, *a, **k)
    monkeypatch.setattr(builtins, "__import__", sem_pacote)
    assert c.disponivel() is False and "ImportError" in c.erro
    ind = rag.IndiceSemantico()
    ind.construir(TRECHOS, np.ones((3, 3), dtype=np.float32))
    assert ind.buscar("clorofila", k=1)[0].trecho_id == 0  # cai no TF-IDF


def test_prefixos_e5():
    assert rag.CodificadorEmbeddings("intfloat/multilingual-e5-small")._prefixo("query") == "query: "
    assert rag.CodificadorEmbeddings("outro-modelo")._prefixo("query") == ""


def test_vetor_ida_e_volta_em_bytes():
    v = np.array([0.1, -0.5, 2.0], dtype=np.float32)
    assert np.allclose(rag.bytes_para_vetor(rag.vetor_para_bytes(v)), v)


def test_reconstruir_indice_grava_embeddings_no_banco(falso):
    from app.db import SessionLocal
    from app.models import TrechoMaterial
    with SessionLocal() as db:
        rag.reconstruir_indice(db)
        trechos = db.query(TrechoMaterial).all()
        assert trechos and all(t.embedding and t.embedding_modelo == "falso" for t in trechos)
    assert rag.indice.modo.startswith("híbrida")
    rag.indice.construir([], None)


def test_migracao_acrescenta_colunas_em_banco_da_v010(tmp_path, monkeypatch):
    from app import db as modulo_db
    eng = create_engine(f"sqlite:///{tmp_path}/antigo.db")
    with eng.begin() as con:  # tabela como era na v0.1.0, sem as colunas novas
        con.execute(text("CREATE TABLE trecho_material (id INTEGER PRIMARY KEY, "
                         "material_id INTEGER, ordem INTEGER, texto TEXT)"))
    monkeypatch.setattr(modulo_db, "engine", eng)
    modulo_db.migrar()
    colunas = {c["name"] for c in inspect(eng).get_columns("trecho_material")}
    assert {"embedding", "embedding_modelo"} <= colunas
    modulo_db.migrar()  # rodar de novo não pode falhar
