"""EduMindAI — aplicação web (MVP).

Executar:  uvicorn app.main:app --reload
"""
import os
from contextlib import asynccontextmanager
import secrets
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from starlette.middleware.sessions import SessionMiddleware

from . import rag, seguranca
from .alertas import avaliar_checkin
from .db import SessionLocal, criar_tabelas, get_db
from .models import (PERFIS_SENSORIAIS, Adaptacao, Alerta, CheckIn, Estudante, LogAcesso,
                     Material, TrechoMaterial, Turma, Usuario)
from .sentimento import analisar

BASE = Path(__file__).parent


@asynccontextmanager
async def ciclo_de_vida(_app):
    criar_tabelas()
    with SessionLocal() as db:
        rag.reconstruir_indice(db)
    yield


app = FastAPI(title="EduMindAI", docs_url=None, redoc_url=None, lifespan=ciclo_de_vida)
app.add_middleware(SessionMiddleware,
                   secret_key=os.getenv("EDUMIND_SEGREDO_SESSAO", secrets.token_urlsafe(32)),
                   session_cookie="edumind_sessao", max_age=60 * 60 * 8,
                   same_site="lax", https_only=os.getenv("EDUMIND_HTTPS") == "1")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")

HUMORES = {1: ("😢", "Muito mal"), 2: ("🙁", "Mal"), 3: ("😐", "Mais ou menos"),
           4: ("🙂", "Bem"), 5: ("😄", "Muito bem")}
templates.env.globals["HUMORES"] = HUMORES


@app.middleware("http")
async def cabecalhos_seguranca(request: Request, call_next):
    resp: Response = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "same-origin"
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
        "form-action 'self'; frame-ancestors 'none'")
    return resp




# ------------------------------------------------------------------ utilitários ------------
class NaoAutenticado(Exception):
    pass


@app.exception_handler(NaoAutenticado)
async def _redir_login(request: Request, exc: NaoAutenticado):
    return RedirectResponse("/login", status_code=303)


def usuario_atual(request: Request, db=Depends(get_db)) -> Usuario:
    uid = request.session.get("uid")
    usuario = db.get(Usuario, uid) if uid else None
    if not usuario or not usuario.ativo:
        raise NaoAutenticado()
    return usuario


def exigir(*perfis):
    def dep(usuario: Usuario = Depends(usuario_atual)) -> Usuario:
        if usuario.perfil not in perfis:
            raise HTTPException(403, "Acesso não permitido para este perfil.")
        return usuario
    return dep


def render(request: Request, nome: str, usuario: Usuario | None = None, **ctx):
    ctx.update(request=request, usuario=usuario,
               csrf=seguranca.token_csrf(request.session),
               aviso=request.session.pop("aviso", None))
    return templates.TemplateResponse(request, nome, ctx)


def checar_csrf(request: Request, token: str):
    if not seguranca.csrf_valido(request.session, token):
        raise HTTPException(400, "Sessão expirada. Recarregue a página e tente novamente.")


def avisar(request: Request, texto: str):
    request.session["aviso"] = texto


# ------------------------------------------------------------------ autenticação (RF001) ---
@app.get("/", include_in_schema=False)
def inicio(usuario: Usuario = Depends(usuario_atual)):
    return RedirectResponse({"aluno": "/aluno", "professor": "/professor",
                             "gestor": "/gestor"}[usuario.perfil], status_code=303)


@app.get("/login", response_class=HTMLResponse)
def tela_login(request: Request):
    return render(request, "login.html")


@app.post("/login")
def fazer_login(request: Request, email: str = Form(...), senha: str = Form(...),
                csrf: str = Form(""), db=Depends(get_db)):
    checar_csrf(request, csrf)
    chave = email.strip().lower()
    if seguranca.login_bloqueado(chave):
        return render(request, "login.html", erro="Muitas tentativas. Aguarde 5 minutos.",
                      email=email)
    usuario = db.scalar(select(Usuario).where(Usuario.email == chave))
    if not usuario or not usuario.ativo or not seguranca.verificar_senha(senha, usuario.senha_hash):
        seguranca.registrar_falha_login(chave)
        seguranca.auditar(db, None, "login_falhou", chave[:2] + "***@" + chave.partition("@")[2])
        return render(request, "login.html", erro="E-mail ou senha incorretos.", email=email)
    seguranca.limpar_falhas_login(chave)
    request.session.clear()
    request.session["uid"] = usuario.id
    seguranca.auditar(db, usuario.id, "login", usuario.perfil)
    return RedirectResponse("/", status_code=303)


@app.post("/sair")
def sair(request: Request, csrf: str = Form("")):
    checar_csrf(request, csrf)
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.post("/preferencias")
def preferencias(request: Request, csrf: str = Form(""), fonte_grande: str = Form(None),
                 alto_contraste: str = Form(None), espacamento: str = Form(None),
                 voltar: str = Form("/"), usuario: Usuario = Depends(usuario_atual),
                 db=Depends(get_db)):
    checar_csrf(request, csrf)
    usuario.pref_fonte_grande = bool(fonte_grande)
    usuario.pref_alto_contraste = bool(alto_contraste)
    usuario.pref_espacamento = bool(espacamento)
    db.merge(usuario); db.commit()
    avisar(request, "Preferências de leitura salvas.")
    return RedirectResponse(voltar if voltar.startswith("/") else "/", status_code=303)


# ------------------------------------------------------------------ aluno: check-in (RF003)
@app.get("/aluno", response_class=HTMLResponse)
def painel_aluno(request: Request, usuario: Usuario = Depends(exigir("aluno")), db=Depends(get_db)):
    est = usuario.estudante
    hoje = db.scalar(select(CheckIn).where(CheckIn.estudante_id == est.id, CheckIn.data == date.today()))
    semana = db.scalars(select(CheckIn).where(CheckIn.estudante_id == est.id,
                                              CheckIn.data >= date.today() - timedelta(days=6))
                        .order_by(CheckIn.data)).all()
    return render(request, "aluno_checkin.html", usuario, hoje=hoje, semana=semana,
                  consentimento=est.consentimento_responsavel)


@app.post("/aluno/checkin")
def registrar_checkin(request: Request, humor: int = Form(...), comentario: str = Form(""),
                      csrf: str = Form(""), usuario: Usuario = Depends(exigir("aluno")),
                      db=Depends(get_db)):
    checar_csrf(request, csrf)
    est = usuario.estudante
    if not est.consentimento_responsavel:
        raise HTTPException(403, "Check-in disponível após o consentimento do responsável.")
    if humor not in HUMORES:
        raise HTTPException(422, "Opção de humor inválida.")
    comentario = comentario.strip()[:500]
    r = analisar(humor, comentario)
    ck = db.scalar(select(CheckIn).where(CheckIn.estudante_id == est.id, CheckIn.data == date.today()))
    if ck is None:
        ck = CheckIn(estudante_id=est.id, data=date.today())
        db.add(ck)
    ck.humor, ck.comentario_cifrado = humor, seguranca.cifrar(comentario)
    ck.sentimento_score, ck.sentimento_rotulo, ck.sinal_risco = r.score, r.rotulo, r.sinal_risco
    db.commit()
    avaliar_checkin(db, est, ck)
    avisar(request, "Obrigado por contar como você está! Seu check-in foi registrado.")
    return RedirectResponse("/aluno", status_code=303)


# ------------------------------------------------------------------ aluno: materiais (RF002)
def _material_da_turma(db, material_id: int, est: Estudante) -> Material:
    m = db.get(Material, material_id)
    if not m or m.turma_id != est.turma_id:
        raise HTTPException(404, "Material não encontrado.")
    return m


def obter_adaptacao(db, material: Material, perfil: str) -> Adaptacao:
    ad = db.scalar(select(Adaptacao).where(Adaptacao.material_id == material.id,
                                           Adaptacao.perfil_sensorial == perfil))
    if ad is None:
        html_, metodo = rag.adaptar(material.titulo, material.texto_original, perfil)
        ad = Adaptacao(material_id=material.id, perfil_sensorial=perfil,
                       conteudo_html=html_, metodo=metodo)
        db.add(ad); db.commit()
    return ad


@app.get("/aluno/materiais", response_class=HTMLResponse)
def materiais_aluno(request: Request, usuario: Usuario = Depends(exigir("aluno")), db=Depends(get_db)):
    mats = db.scalars(select(Material).where(Material.turma_id == usuario.estudante.turma_id)
                      .order_by(Material.criado_em.desc())).all()
    return render(request, "aluno_materiais.html", usuario, materiais=mats)


@app.get("/aluno/materiais/{material_id}", response_class=HTMLResponse)
def ver_material(material_id: int, request: Request, usuario: Usuario = Depends(exigir("aluno")),
                 db=Depends(get_db)):
    est = usuario.estudante
    m = _material_da_turma(db, material_id, est)
    ad = obter_adaptacao(db, m, est.perfil_sensorial)
    return render(request, "aluno_material.html", usuario, material=m, adaptacao=ad,
                  perfil=est.perfil_sensorial, descricao=rag.DESCRICAO_PERFIL[est.perfil_sensorial])


@app.post("/aluno/materiais/{material_id}/perguntar", response_class=HTMLResponse)
def perguntar(material_id: int, request: Request, pergunta: str = Form(...), csrf: str = Form(""),
              usuario: Usuario = Depends(exigir("aluno")), db=Depends(get_db)):
    checar_csrf(request, csrf)
    est = usuario.estudante
    m = _material_da_turma(db, material_id, est)
    ad = obter_adaptacao(db, m, est.perfil_sensorial)
    resposta, achados, ms = rag.responder_pergunta(pergunta[:300], est.perfil_sensorial, m.id)
    return render(request, "aluno_material.html", usuario, material=m, adaptacao=ad,
                  perfil=est.perfil_sensorial, descricao=rag.DESCRICAO_PERFIL[est.perfil_sensorial],
                  pergunta=pergunta, resposta=resposta, achados=achados, tempo_busca=ms)


# ------------------------------------------------------------------ titular dos dados (LGPD)
@app.get("/meus-dados", response_class=HTMLResponse)
def meus_dados(request: Request, usuario: Usuario = Depends(usuario_atual)):
    return render(request, "meus_dados.html", usuario)


@app.get("/meus-dados/exportar")
def exportar_dados(usuario: Usuario = Depends(usuario_atual), db=Depends(get_db)):
    dados = {"nome": usuario.nome, "email": usuario.email, "perfil": usuario.perfil,
             "criado_em": usuario.criado_em.isoformat()}
    if usuario.estudante:
        est = usuario.estudante
        dados["perfil_sensorial"] = est.perfil_sensorial
        dados["turma"] = est.turma.nome
        dados["checkins"] = [{"data": c.data.isoformat(), "humor": c.humor,
                              "comentario": seguranca.decifrar(c.comentario_cifrado),
                              "sentimento": c.sentimento_rotulo} for c in est.checkins]
    seguranca.auditar(db, usuario.id, "exportou_proprios_dados", f"usuario:{usuario.id}")
    return JSONResponse(dados, headers={
        "Content-Disposition": 'attachment; filename="meus-dados-edumindai.json"'})


# ------------------------------------------------------------------ professor (RF004) -------
def _turmas_do_prof(db, prof: Usuario) -> list[Turma]:
    return db.scalars(select(Turma).where(Turma.professor_id == prof.id)).all()


@app.get("/professor", response_class=HTMLResponse)
def painel_professor(request: Request, usuario: Usuario = Depends(exigir("professor")),
                     db=Depends(get_db)):
    turmas = _turmas_do_prof(db, usuario)
    ids_turma = [t.id for t in turmas]
    estudantes = db.scalars(select(Estudante).where(Estudante.turma_id.in_(ids_turma))).all()
    linhas = []
    for e in estudantes:
        ultimos = e.checkins[:5]
        abertos = db.scalar(select(func.count(Alerta.id)).where(
            Alerta.estudante_id == e.id, Alerta.status != "resolvido"))
        linhas.append({"est": e, "ultimos": list(reversed(ultimos)), "alertas": abertos})
    linhas.sort(key=lambda l: (-l["alertas"], l["est"].usuario.nome))
    hoje = date.today()
    feitos_hoje = sum(1 for l in linhas if l["ultimos"] and l["ultimos"][-1].data == hoje)
    dist = Counter(c.sentimento_rotulo for e in estudantes for c in e.checkins
                   if c.data >= hoje - timedelta(days=6))
    total_alertas = sum(l["alertas"] for l in linhas)
    return render(request, "prof_painel.html", usuario, turmas=turmas, linhas=linhas,
                  feitos_hoje=feitos_hoje, dist=dist, total_alertas=total_alertas)


@app.get("/professor/alertas", response_class=HTMLResponse)
def alertas_professor(request: Request, usuario: Usuario = Depends(exigir("professor")),
                      db=Depends(get_db)):
    ids_turma = [t.id for t in _turmas_do_prof(db, usuario)]
    alertas = db.scalars(select(Alerta).join(Estudante).where(Estudante.turma_id.in_(ids_turma))
                         .order_by((Alerta.status == "resolvido"), Alerta.nivel, Alerta.criado_em.desc())).all()
    comentarios = {}
    for a in alertas:
        if a.status != "resolvido" and a.checkin_id:
            ck = db.get(CheckIn, a.checkin_id)
            comentarios[a.id] = seguranca.decifrar(ck.comentario_cifrado) if ck else None
    if comentarios:
        seguranca.auditar(db, usuario.id, "visualizou_comentarios_alerta",
                          ",".join(str(i) for i in comentarios))
    return render(request, "prof_alertas.html", usuario, alertas=alertas, comentarios=comentarios)


@app.post("/professor/alertas/{alerta_id}")
def atualizar_alerta(alerta_id: int, request: Request, status: str = Form(...),
                     observacao: str = Form(""), csrf: str = Form(""),
                     usuario: Usuario = Depends(exigir("professor")), db=Depends(get_db)):
    checar_csrf(request, csrf)
    a = db.get(Alerta, alerta_id)
    if not a or a.estudante.turma.professor_id != usuario.id:
        raise HTTPException(404, "Alerta não encontrado.")
    if status not in ("aberto", "em_acomp", "resolvido"):
        raise HTTPException(422, "Status inválido.")
    a.status, a.observacao, a.atualizado_por = status, observacao.strip()[:1000] or a.observacao, usuario.id
    db.commit()
    seguranca.auditar(db, usuario.id, f"alerta_{status}", f"alerta:{a.id}")
    avisar(request, "Alerta atualizado.")
    return RedirectResponse("/professor/alertas", status_code=303)


@app.get("/professor/materiais", response_class=HTMLResponse)
def materiais_professor(request: Request, usuario: Usuario = Depends(exigir("professor")),
                        db=Depends(get_db)):
    mats = db.scalars(select(Material).where(Material.professor_id == usuario.id)
                      .order_by(Material.criado_em.desc())).all()
    return render(request, "prof_materiais.html", usuario, materiais=mats,
                  turmas=_turmas_do_prof(db, usuario))


@app.post("/professor/materiais")
def novo_material(request: Request, titulo: str = Form(...), disciplina: str = Form(...),
                  turma_id: int = Form(...), texto: str = Form(...), csrf: str = Form(""),
                  usuario: Usuario = Depends(exigir("professor")), db=Depends(get_db)):
    checar_csrf(request, csrf)
    if turma_id not in [t.id for t in _turmas_do_prof(db, usuario)]:
        raise HTTPException(403, "Turma não pertence ao professor.")
    texto = texto.strip()
    if len(texto.split()) < 20:
        avisar(request, "O texto precisa ter pelo menos 20 palavras.")
        return RedirectResponse("/professor/materiais", status_code=303)
    m = Material(titulo=titulo.strip()[:160], disciplina=disciplina.strip()[:60],
                 turma_id=turma_id, professor_id=usuario.id, texto_original=texto[:50000])
    db.add(m); db.flush()
    for i, t in enumerate(rag.dividir_em_trechos(texto)):
        db.add(TrechoMaterial(material_id=m.id, ordem=i, texto=t))
    db.commit()
    rag.reconstruir_indice(db)
    avisar(request, f"Material “{m.titulo}” publicado e indexado ({len(m.trechos)} trechos).")
    return RedirectResponse(f"/professor/materiais/{m.id}", status_code=303)


@app.get("/professor/materiais/{material_id}", response_class=HTMLResponse)
def previa_material(material_id: int, request: Request, perfil: str = "TDAH",
                    usuario: Usuario = Depends(exigir("professor")), db=Depends(get_db)):
    m = db.get(Material, material_id)
    if not m or m.professor_id != usuario.id:
        raise HTTPException(404, "Material não encontrado.")
    perfil = perfil if perfil in PERFIS_SENSORIAIS else "TDAH"
    ad = obter_adaptacao(db, m, perfil)
    return render(request, "prof_material.html", usuario, material=m, adaptacao=ad, perfil=perfil,
                  perfis=PERFIS_SENSORIAIS, descricao=rag.DESCRICAO_PERFIL[perfil])


# ------------------------------------------------------------------ gestor ------------------
@app.get("/gestor", response_class=HTMLResponse)
def painel_gestor(request: Request, usuario: Usuario = Depends(exigir("gestor")), db=Depends(get_db)):
    hoje = date.today()
    resumo = []
    for t in db.scalars(select(Turma)).all():
        ids = [e.id for e in t.estudantes]
        cks = db.scalars(select(CheckIn).where(CheckIn.estudante_id.in_(ids),
                                               CheckIn.data >= hoje - timedelta(days=29))).all()
        n = len(cks)
        resumo.append({
            "turma": t, "estudantes": len(ids),
            "adesao": (len({(c.estudante_id, c.data) for c in cks}) / (len(ids) * 30) * 100) if ids else 0,
            "checkins": n,
            "pct_neg": (sum(c.sentimento_rotulo == "negativo" for c in cks) / n * 100) if n else 0,
            "alertas_abertos": db.scalar(select(func.count(Alerta.id)).where(
                Alerta.estudante_id.in_(ids), Alerta.status != "resolvido")),
            "materiais": db.scalar(select(func.count(Material.id)).where(Material.turma_id == t.id)),
        })
    logs = db.scalars(select(LogAcesso).order_by(LogAcesso.data_hora.desc()).limit(15)).all()
    return render(request, "gestor_painel.html", usuario, resumo=resumo, logs=logs)


@app.get("/saude")
def saude():
    return {"status": "ok", "hora": datetime.now().isoformat(timespec="seconds")}
