"""Motor de análise de sentimento dos check-ins (RF004).

Combina a escala de humor escolhida pelo estudante (1 a 5) com um léxico de polaridade em
português. Versão 2 (release 0.2.0), além da negação e dos intensificadores da v1:
  - contraste: em "X mas Y" a parte depois do "mas" pesa mais (é a conclusão da frase);
  - atenuadores: "meio", "um pouco" reduzem a força da palavra seguinte;
  - negação de palavra negativa ("não foi ruim") vira positivo fraco, não positivo pleno;
  - expressões de várias palavras ("tudo bem", "de boa", "nada demais", "mais ou menos");
  - léxico ampliado com gírias e palavras do cotidiano escolar.
A interface `analisar()` não mudou, então um modelo Transformer (ex.: BERTimbau ajustado com
dados reais) pode substituir este módulo sem afetar o resto do sistema.
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
    # v0.2.0
    "curti", "curtir", "maneiro", "suave", "ajudou", "ajudaram", "orgulhoso", "orgulhosa",
    "brinquei", "brincamos", "divertiu", "sorte", "venci", "ganhei", "carinho",
}
NEGATIVAS = {
    "triste", "mal", "ruim", "chateado", "chateada", "cansado", "cansada", "ansioso",
    "ansiosa", "nervoso", "nervosa", "medo", "raiva", "bravo", "brava", "sozinho", "sozinha",
    "chorei", "chorando", "choro", "dificil", "odeio", "pior", "preocupado", "preocupada",
    "estressado", "estressada", "cansativo", "confuso", "confusa", "irritado", "irritada",
    "vergonha", "frustrado", "frustrada", "brigaram", "briga", "bullying", "zoaram",
    "zoando", "excluido", "excluida", "doente", "dor", "sono", "perdido", "perdida", "chato",
    # v0.2.0
    "briguei", "brigou", "zoado", "zoada", "entediado", "entediada", "tedio", "pessimo",
    "pessima", "horrivel", "machucou", "machuquei", "doeu", "assustado", "assustada",
    "chata", "sozinhos", "ignoraram", "chorar",
}
# palavras de peso menor (tristeza leve, não sofrimento)
PESOS_LEXICO = {"saudade": -0.5, "saudades": -0.5, "sono": -0.5, "cansado": -0.7,
                "cansada": -0.7}
EXPRESSOES = {  # expressões avaliadas antes das palavras isoladas
    "tudo bem": 0.6, "tudo certo": 0.7, "deu certo": 0.7, "de boa": 0.6, "da hora": 0.8,
    "nada demais": 0.0, "mais ou menos": 0.0, "tanto faz": 0.0,
}
CONTRASTES = ("mas", "porem", "so que", "entretanto", "contudo")
PESO_ANTES_CONTRASTE, PESO_DEPOIS_CONTRASTE = 0.5, 1.5
ATENUADORES = {"meio": 0.5, "pouco": 0.5, "levemente": 0.5}
FORCA_NEGACAO_DE_NEGATIVO = 0.3  # "não foi ruim" ≈ levemente positivo
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


def _segmentos(texto_norm: str) -> list[tuple[str, float]]:
    """Divide no último conector de contraste: [(antes, peso), (depois, peso)]."""
    padrao = r"\b(" + "|".join(CONTRASTES) + r")\b"
    partes = re.split(padrao, texto_norm)
    if len(partes) < 3:
        return [(texto_norm, 1.0)]
    antes = " ".join(p for p in partes[:-2] if p not in CONTRASTES)
    return [(antes, PESO_ANTES_CONTRASTE), (partes[-1], PESO_DEPOIS_CONTRASTE)]


def _valores_segmento(seg: str) -> list[float]:
    valores = []
    for exp, v in EXPRESSOES.items():
        if re.search(rf"\b{exp}\b", seg):
            valores.append(v)
            seg = re.sub(rf"\b{exp}\b", " ", seg)
    # vírgula e ponto encerram o alcance da negação
    for oracao in re.split(r"[,.;!?]", seg):
        tokens = re.findall(r"[a-z]+", oracao)
        for i, tok in enumerate(tokens):
            if tok in PESOS_LEXICO:
                valor = PESOS_LEXICO[tok]
            elif tok in POSITIVAS:
                valor = 1.0
            elif tok in NEGATIVAS:
                valor = -1.0
            else:
                continue
            janela = tokens[max(0, i - 3):i]
            if any(t in NEGADORES for t in janela):
                valor = FORCA_NEGACAO_DE_NEGATIVO if valor < 0 else -0.8 * valor
            for t in janela:
                valor *= INTENSIFICADORES.get(t, 1.0) * ATENUADORES.get(t, 1.0)
            valores.append(valor)
    return valores


def polaridade_texto(texto: str) -> float | None:
    """Retorna polaridade em [-1, 1] ou None se o texto não tiver palavras de opinião."""
    soma, pesos = 0.0, 0.0
    for seg, peso in _segmentos(normalizar(texto)):
        for v in _valores_segmento(seg):
            soma += v * peso
            pesos += peso
    if not pesos:
        return None
    return max(-1.0, min(1.0, soma / pesos))


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
