"""Testes de integração das telas novas da release 0.2.0 (RF009 e RF010)."""
import io
import re
from datetime import date, timedelta

from docx import Document
from sqlalchemy import select

from app import seguranca
from app.db import SessionLocal
from app.models import Estudante, LogAcesso, Material, Turma, Usuario

from .conftest import csrf_de

TEXTO = ("A Lua é o satélite natural da Terra. Ela não tem luz própria e brilha porque "
         "reflete a luz do Sol. As fases da Lua mudam conforme a parte iluminada que vemos.")


def _turma_do_professor():
    with SessionLocal() as db:
        prof = db.scalar(select(Usuario).where(Usuario.email == "professor@escola.demo"))
        return db.scalar(select(Turma).where(Turma.professor_id == prof.id)).id


def _cadastrar(cliente, email, perfil="TEA"):
    token = csrf_de(cliente.get("/professor/turmas").text)
    return cliente.post("/professor/estudantes", data={
        "nome": "Estudante Teste", "email": email, "turma_id": _turma_do_professor(),
        "perfil_sensorial": perfil, "csrf": token})


def test_professor_cadastra_estudante_e_recebe_senha_provisoria(cliente, entrar):
    entrar("professor@escola.demo")
    r = _cadastrar(cliente, "novo1@escola.demo")
    assert r.status_code == 200 and "Senha provisória" in r.text
    senha = re.search(r'class="senha">([^<]+)<', r.text).group(1)
    with SessionLocal() as db:
        u = db.scalar(select(Usuario).where(Usuario.email == "novo1@escola.demo"))
        assert u.perfil == "aluno" and senha not in u.senha_hash
        assert seguranca.verificar_senha(senha, u.senha_hash)
        assert u.estudante.consentimento_responsavel is False
    # a senha não pode ficar no cookie de sessão
    assert senha not in str(cliente.cookies.get("edumind_sessao", ""))


def test_estudante_sem_consentimento_nao_faz_checkin_ate_o_registro(cliente, entrar):
    entrar("professor@escola.demo")
    r = _cadastrar(cliente, "novo2@escola.demo")
    senha = re.search(r'class="senha">([^<]+)<', r.text).group(1)
    with SessionLocal() as db:
        est_id = db.scalar(select(Usuario).where(Usuario.email == "novo2@escola.demo")).estudante.id

    # tentativa de registrar sem confirmar o arquivamento do termo é recusada
    token = csrf_de(cliente.get("/professor/turmas").text)
    cliente.post(f"/professor/estudantes/{est_id}/consentimento", data={
        "nome_responsavel": "Maria Teste", "data_termo": date.today().isoformat(), "csrf": token})
    with SessionLocal() as db:
        assert db.get(Estudante, est_id).consentimento_responsavel is False

    token = csrf_de(cliente.get("/professor/turmas").text)
    cliente.post(f"/professor/estudantes/{est_id}/consentimento", data={
        "nome_responsavel": "Maria Teste", "data_termo": date.today().isoformat(),
        "termo_arquivado": "1", "csrf": token})
    with SessionLocal() as db:
        e = db.get(Estudante, est_id)
        assert e.consentimento_responsavel and e.nome_responsavel == "Maria Teste"
        assert db.scalar(select(LogAcesso).where(LogAcesso.acao == "registrou_consentimento",
                                                 LogAcesso.recurso == f"estudante:{est_id}"))

    cliente.cookies.clear()
    entrar("novo2@escola.demo", senha)
    token = csrf_de(cliente.get("/aluno").text)
    assert cliente.post("/aluno/checkin", data={"humor": 4, "csrf": token}).status_code == 200


def test_data_do_termo_no_futuro_e_recusada(cliente, entrar):
    entrar("professor@escola.demo")
    _cadastrar(cliente, "novo3@escola.demo")
    with SessionLocal() as db:
        est_id = db.scalar(select(Usuario).where(Usuario.email == "novo3@escola.demo")).estudante.id
    token = csrf_de(cliente.get("/professor/turmas").text)
    cliente.post(f"/professor/estudantes/{est_id}/consentimento", data={
        "nome_responsavel": "X", "data_termo": (date.today() + timedelta(days=3)).isoformat(),
        "termo_arquivado": "1", "csrf": token})
    with SessionLocal() as db:
        assert db.get(Estudante, est_id).consentimento_responsavel is False


def test_revogacao_bloqueia_novos_checkins(cliente, entrar):
    entrar("professor@escola.demo")
    with SessionLocal() as db:
        est = db.scalar(select(Usuario).where(Usuario.email == "heitor@escola.demo")).estudante
    token = csrf_de(cliente.get("/professor/turmas").text)
    cliente.post(f"/professor/estudantes/{est.id}/revogar", data={"csrf": token})
    cliente.cookies.clear()
    entrar("heitor@escola.demo")
    token = csrf_de(cliente.get("/aluno").text)
    assert cliente.post("/aluno/checkin", data={"humor": 4, "csrf": token}).status_code == 403


def test_professor_altera_perfil_de_leitura(cliente, entrar):
    entrar("professor@escola.demo")
    with SessionLocal() as db:
        est_id = db.scalar(select(Usuario).where(Usuario.email == "davi@escola.demo")).estudante.id
    token = csrf_de(cliente.get("/professor/turmas").text)
    cliente.post(f"/professor/estudantes/{est_id}/perfil",
                 data={"perfil_sensorial": "DISLEXIA", "csrf": token})
    with SessionLocal() as db:
        assert db.get(Estudante, est_id).perfil_sensorial == "DISLEXIA"


def test_email_repetido_nao_cria_outro_usuario(cliente, entrar):
    entrar("professor@escola.demo")
    r = _cadastrar(cliente, "ana@escola.demo")
    assert "Já existe um usuário com este e-mail" in r.text


def test_professor_cria_turma(cliente, entrar):
    entrar("professor@escola.demo")
    token = csrf_de(cliente.get("/professor/turmas").text)
    cliente.post("/professor/turmas", data={"nome": "6º ano C", "escola": "Escola Teste",
                                             "ano_letivo": 2026, "csrf": token})
    assert "6º ano C" in cliente.get("/professor/turmas").text


def test_outro_professor_nao_altera_estudante_alheio(cliente, entrar):
    with SessionLocal() as db:
        outro = Usuario(nome="Outra Prof", email="outra@escola.demo", perfil="professor",
                        senha_hash=seguranca.gerar_hash_senha("edumind123"))
        db.add(outro); db.commit()
        est_id = db.scalar(select(Usuario).where(Usuario.email == "ana@escola.demo")).estudante.id
    entrar("outra@escola.demo")
    token = csrf_de(cliente.get("/professor/turmas").text)
    r = cliente.post(f"/professor/estudantes/{est_id}/perfil",
                     data={"perfil_sensorial": "TEA", "csrf": token})
    assert r.status_code == 404


def _docx(texto):
    buf = io.BytesIO()
    d = Document()
    for p in texto.split(". "):
        d.add_paragraph(p)
    d.save(buf)
    return buf.getvalue()


def test_importa_material_de_docx(cliente, entrar):
    entrar("professor@escola.demo")
    token = csrf_de(cliente.get("/professor/materiais").text)
    r = cliente.post("/professor/materiais",
                     data={"titulo": "A Lua", "disciplina": "Ciências",
                           "turma_id": _turma_do_professor(), "csrf": token},
                     files={"arquivo": ("lua.docx", _docx(TEXTO),
                                        "application/vnd.openxmlformats-officedocument."
                                        "wordprocessingml.document")})
    assert r.status_code == 200
    with SessionLocal() as db:
        m = db.scalar(select(Material).where(Material.titulo == "A Lua"))
        assert m.origem == "lua.docx" and "satélite natural" in m.texto_original and m.trechos


def test_importa_txt_e_recusa_formato_nao_aceito(cliente, entrar):
    entrar("professor@escola.demo")
    token = csrf_de(cliente.get("/professor/materiais").text)
    r = cliente.post("/professor/materiais",
                     data={"titulo": "Lua txt", "disciplina": "Ciências",
                           "turma_id": _turma_do_professor(), "csrf": token},
                     files={"arquivo": ("lua.txt", TEXTO.encode("utf-8"), "text/plain")})
    assert r.status_code == 200
    token = csrf_de(cliente.get("/professor/materiais").text)
    r = cliente.post("/professor/materiais",
                     data={"titulo": "Planilha", "disciplina": "Ciências",
                           "turma_id": _turma_do_professor(), "csrf": token},
                     files={"arquivo": ("dados.xlsx", b"PK\x03\x04", "application/octet-stream")})
    assert "Formato não aceito" in r.text
    with SessionLocal() as db:
        assert db.scalar(select(Material).where(Material.titulo == "Lua txt"))
        assert not db.scalar(select(Material).where(Material.titulo == "Planilha"))


def test_saude_informa_versao(cliente):
    from app import __version__
    assert cliente.get("/saude").json()["versao"] == __version__ == "0.2.0"
