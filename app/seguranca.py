"""Segurança: hash de senha, criptografia de dados sensíveis, CSRF e auditoria."""
import base64
import hashlib
import hmac
import os
import secrets
import time
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from .models import LogAcesso

# ---------------- Senhas (PBKDF2-SHA256, 310 mil iterações — recomendação OWASP) -------------
_ITERACOES = 310_000


def gerar_hash_senha(senha: str) -> str:
    sal = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", senha.encode(), sal, _ITERACOES)
    return f"pbkdf2_sha256${_ITERACOES}${base64.b64encode(sal).decode()}${base64.b64encode(dk).decode()}"


def verificar_senha(senha: str, armazenado: str) -> bool:
    try:
        _, it, sal_b64, dk_b64 = armazenado.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", senha.encode(), base64.b64decode(sal_b64), int(it))
        return hmac.compare_digest(dk, base64.b64decode(dk_b64))
    except (ValueError, TypeError):
        return False


# ---------------- Criptografia em repouso (comentários dos check-ins) -------------------------
def _carregar_chave() -> bytes:
    chave = os.getenv("EDUMIND_CHAVE_DADOS")
    if chave:
        return chave.encode()
    arquivo = Path(os.getenv("EDUMIND_ARQ_CHAVE", ".chave_dados"))
    if not arquivo.exists():
        arquivo.write_bytes(Fernet.generate_key())
        try:
            arquivo.chmod(0o600)
        except OSError:
            pass
    return arquivo.read_bytes().strip()


_fernet = Fernet(_carregar_chave())


def cifrar(texto: str | None) -> str | None:
    if not texto:
        return None
    return _fernet.encrypt(texto.encode()).decode()


def decifrar(token: str | None) -> str | None:
    if not token:
        return None
    try:
        return _fernet.decrypt(token.encode()).decode()
    except InvalidToken:
        return "[conteúdo indisponível]"


# ---------------- CSRF ------------------------------------------------------------------------
def token_csrf(sessao: dict) -> str:
    if "csrf" not in sessao:
        sessao["csrf"] = secrets.token_urlsafe(32)
    return sessao["csrf"]


def csrf_valido(sessao: dict, recebido: str | None) -> bool:
    esperado = sessao.get("csrf")
    return bool(esperado and recebido and hmac.compare_digest(esperado, recebido))


# ---------------- Limite de tentativas de login (força bruta) --------------------------------
_tentativas: dict[str, list[float]] = {}
MAX_TENTATIVAS, JANELA_S = 5, 300


def login_bloqueado(chave: str) -> bool:
    agora = time.time()
    hist = [t for t in _tentativas.get(chave, []) if agora - t < JANELA_S]
    _tentativas[chave] = hist
    return len(hist) >= MAX_TENTATIVAS


def registrar_falha_login(chave: str) -> None:
    _tentativas.setdefault(chave, []).append(time.time())


def limpar_falhas_login(chave: str) -> None:
    _tentativas.pop(chave, None)


# ---------------- Auditoria -------------------------------------------------------------------
def auditar(db, usuario_id: int | None, acao: str, recurso: str) -> None:
    db.add(LogAcesso(usuario_id=usuario_id, acao=acao, recurso=recurso))
    db.commit()
