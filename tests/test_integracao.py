"""Testes de integração: fluxos completos pela aplicação web."""
from sqlalchemy import select, text

from app.db import SessionLocal
from app.models import Alerta, CheckIn, Estudante, LogAcesso, Usuario

from .conftest import csrf_de


def test_login_invalido_mostra_erro(entrar):
    r = entrar("professor@escola.demo", "senhaerrada")
    assert "E-mail ou senha incorretos" in r.text


def test_login_redireciona_conforme_perfil(entrar):
    assert entrar("professor@escola.demo").url.path == "/professor"


def test_rota_protegida_sem_login_vai_para_login(cliente):
    r = cliente.get("/professor")
    assert r.url.path == "/login"


def test_aluno_nao_acessa_area_do_professor(cliente, entrar):
    entrar("ana@escola.demo")
    assert cliente.get("/professor").status_code == 403
    assert cliente.get("/gestor").status_code == 403


def test_post_sem_csrf_e_recusado(cliente, entrar):
    entrar("ana@escola.demo")
    r = cliente.post("/aluno/checkin", data={"humor": 4, "csrf": "falso"})
    assert r.status_code == 400


def test_bloqueio_apos_tentativas(entrar):
    for _ in range(5):
        entrar("davi@escola.demo", "x")
    assert "Muitas tentativas" in entrar("davi@escola.demo").text


def test_checkin_grava_comentario_cifrado(cliente, entrar):
    entrar("heitor@escola.demo")
    token = csrf_de(cliente.get("/aluno").text)
    cliente.post("/aluno/checkin", data={"humor": 4, "comentario": "aula muito legal hoje", "csrf": token})
    with SessionLocal() as db:
        bruto = db.execute(text("select comentario_cifrado from checkin order by id desc limit 1")).scalar()
    assert bruto and "legal" not in bruto


def test_checkin_de_risco_gera_alerta_alto(cliente, entrar):
    entrar("bruno@escola.demo")
    token = csrf_de(cliente.get("/aluno").text)
    cliente.post("/aluno/checkin", data={"humor": 2, "comentario": "ninguém gosta de mim", "csrf": token})
    with SessionLocal() as db:
        est = db.scalar(select(Estudante).join(Usuario).where(Usuario.email == "bruno@escola.demo"))
        alertas = db.scalars(select(Alerta).where(Alerta.estudante_id == est.id)).all()
    assert any(a.nivel == "alto" for a in alertas)


def test_professor_ve_e_resolve_alerta_com_auditoria(cliente, entrar):
    entrar("professor@escola.demo")
    pagina = cliente.get("/professor/alertas").text
    assert "Central de alertas" in pagina
    with SessionLocal() as db:
        alerta = db.scalar(select(Alerta).where(Alerta.status == "aberto"))
    r = cliente.post(f"/professor/alertas/{alerta.id}",
                     data={"status": "resolvido", "observacao": "Conversa com a família", "csrf": csrf_de(pagina)})
    assert r.status_code == 200
    with SessionLocal() as db:
        assert db.get(Alerta, alerta.id).status == "resolvido"
        assert db.scalar(select(LogAcesso).where(LogAcesso.acao == "alerta_resolvido"))


def test_material_adaptado_ao_perfil_do_aluno(cliente, entrar):
    entrar("ana@escola.demo")  # TDAH
    assert "Resumo rápido" in cliente.get("/aluno/materiais/1").text
    cliente.post("/sair", data={"csrf": csrf_de(cliente.get("/aluno").text)})
    entrar("bruno@escola.demo")  # TEA
    assert "Passo a passo" in cliente.get("/aluno/materiais/1").text


def test_pergunta_ao_material_usa_rag(cliente, entrar):
    entrar("carla@escola.demo")
    pag = cliente.get("/aluno/materiais/1").text
    r = cliente.post("/aluno/materiais/1/perguntar", data={"pergunta": "o que é condensação?", "csrf": csrf_de(pag)})
    assert "gotículas" in r.text


def test_professor_publica_material_e_ele_e_indexado(cliente, entrar):
    entrar("professor@escola.demo")
    pag = cliente.get("/professor/materiais").text
    texto = ("Os planetas giram ao redor do Sol em órbitas. A Terra leva um ano para completar uma volta. "
             "Marte é conhecido como planeta vermelho por causa do óxido de ferro em sua superfície.")
    r = cliente.post("/professor/materiais", data={"titulo": "Sistema Solar", "disciplina": "Ciências",
                                                    "turma_id": 1, "texto": texto, "csrf": csrf_de(pag)})
    assert "Sistema Solar" in r.text and "indexado" in r.text


def test_gestor_ve_apenas_dados_agregados(cliente, entrar):
    entrar("gestora@escola.demo")
    pagina = cliente.get("/gestor").text
    assert "5º ano A" in pagina
    assert "Carla Mendes" not in pagina  # nenhum nome de estudante


def test_exportacao_de_dados_do_titular(cliente, entrar):
    entrar("ana@escola.demo")
    dados = cliente.get("/meus-dados/exportar").json()
    assert dados["email"] == "ana@escola.demo" and "checkins" in dados


def test_cabecalhos_de_seguranca(cliente):
    r = cliente.get("/login")
    assert r.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in r.headers["Content-Security-Policy"]
