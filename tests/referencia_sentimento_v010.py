"""Motor de análise de sentimento dos check-ins (RF004).

Versão MVP: combina a escala de humor escolhida pelo estudante (1 a 5) com um léxico
de polaridade em português que trata negação ("não estou bem") e intensificadores
("muito", "super"). A interface `analisar()` é a mesma que o modelo Transformer
(BERTimbau ajustado) usará na próxima iteração, de modo que a troca não afeta o resto
do sistema.
"""
import re
import unicodedata
from dataclasses import dataclass

POSITIVAS = {
    "bem", "feliz", "alegre", "contente", "animado", "animada", "tranquilo", "tranquila",
    "calmo", "calma", "legal", "otimo", "otima", "bom", "boa", "gostei", "gosto", "adorei",
    "amei", "divertido", "divertida", "consegui", "aprendi", "orgulho", "amigos", "amigo",
    "amiga", "melhor", "descansado", "descansada", "seguro", "segura", "confiante", "paz",
    "facil", "entendi", "obrigado", "obrigada", "incrivel", "show", "massa", "top",
}
NEGATIVAS = {
    "triste", "mal", "ruim", "chateado", "chateada", "cansado", "cansada", "ansioso",
    "ansiosa", "nervoso", "nervosa", "medo", "raiva", "bravo", "brava", "sozinho", "sozinha",
    "chorei", "chorando", "choro", "dificil", "odeio", "pior", "preocupado", "preocupada",
    "estressado", "estressada", "cansativo", "confuso", "confusa", "irritado", "irritada",
    "vergonha", "frustrado", "frustrada", "brigaram", "briga", "bullying", "zoaram",
    "zoando", "excluido", "excluida", "doente", "dor", "sono", "perdido", "perdida", "chato",
}
NEGADORES = {"nao", "nem", "nunca", "jamais", "nada"}
INTENSIFICADORES = {"muito": 1.5, "super": 1.5, "demais": 1.5, "bastante": 1.3, "tao": 1.3}

# Expressões que indicam possível situação de risco e geram alerta imediato ao professor,
# independentemente do escore. A escola deve seguir seu protocolo de proteção.
EXPRESSOES_RISCO = [
    "nao aguento mais", "quero sumir", "queria sumir", "ninguem gosta de mim",
    "me machucar", "me bateram", "batem em mim", "tenho medo de ir pra escola",
    "tenho medo de voltar pra casa", "nao quero mais viver", "queria morrer",
    "ninguem se importa", "estao me ameacando",
]

LIMIAR_POSITIVO = 0.2
LIMIAR_NEGATIVO = -0.2


@dataclass
class ResultadoSentimento:
    score: float      # -1 (muito negativo) a +1 (muito positivo)
    rotulo: str       # positivo | neutro | negativo
    sinal_risco: bool
    score_texto: float | None


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip()


def polaridade_texto(texto: str) -> float | None:
    """Retorna polaridade em [-1, 1] ou None se o texto não tiver palavras de opinião."""
    tokens = re.findall(r"[a-z]+", normalizar(texto))
    soma, achados = 0.0, 0
    for i, tok in enumerate(tokens):
        valor = 1.0 if tok in POSITIVAS else -1.0 if tok in NEGATIVAS else 0.0
        if not valor:
            continue
        janela = tokens[max(0, i - 3):i]
        if any(t in NEGADORES for t in janela):
            valor *= -1
        for t in janela:
            valor *= INTENSIFICADORES.get(t, 1.0)
        soma += valor
        achados += 1
    if not achados:
        return None
    return max(-1.0, min(1.0, soma / achados))


def detectar_risco(texto: str) -> bool:
    t = normalizar(texto)
    return any(exp in t for exp in EXPRESSOES_RISCO)


def analisar(humor: int, comentario: str | None = "") -> ResultadoSentimento:
    if humor not in range(1, 6):
        raise ValueError("humor deve estar entre 1 e 5")
    score_humor = (humor - 3) / 2  # 1→-1, 3→0, 5→+1
    comentario = comentario or ""
    score_texto = polaridade_texto(comentario) if comentario.strip() else None
    score = score_humor if score_texto is None else 0.6 * score_humor + 0.4 * score_texto
    risco = detectar_risco(comentario)
    if risco:
        score = min(score, -0.8)
    rotulo = ("positivo" if score >= LIMIAR_POSITIVO
              else "negativo" if score <= LIMIAR_NEGATIVO else "neutro")
    return ResultadoSentimento(round(score, 3), rotulo, risco,
                               None if score_texto is None else round(score_texto, 3))
