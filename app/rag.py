"""Pipeline de Geração Aumentada de Recuperação (RAG) — RF002.

Etapas:
 1. Ingestão  — o professor envia o texto do material; ele é dividido em trechos (chunks).
 2. Indexação — os trechos são vetorizados (TF-IDF nesta versão do MVP).
 3. Recuperação — dada uma pergunta do estudante, recupera os k trechos mais similares
    (similaridade de cosseno).
 4. Geração/adaptação — o conteúdo recuperado é reescrito para o perfil sensorial do
    estudante. Se houver chave de API de LLM configurada (ANTHROPIC_API_KEY), o texto é
    gerado pelo modelo; caso contrário, aplica-se o adaptador por regras, que funciona
    offline e serve de alternativa (fallback).

Na próxima iteração os vetores TF-IDF serão substituídos por embeddings armazenados no
PostgreSQL com pgvector, mantendo as mesmas funções públicas deste módulo.
"""
from __future__ import annotations

import html
import os
import re
import time
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .sentimento import normalizar

STOPWORDS_PT = """a ao aos as até com como da das de dela dele deles depois do dos e é ela
elas ele eles em entre era essa essas esse esses esta estas este estes eu foi for há isso
isto já la lhe mais mas me mesmo meu minha muito na nas nem no nos nós o os ou para pela
pelas pelo pelos por qual quando que quem se sem ser seu sua são só também te tem tu um
uma umas uns você vocês ser são está estão foram pode podem cada sobre outro outra outros
outras ainda assim onde porque""".split()
STOPWORDS_NORM = sorted({normalizar(p) for p in STOPWORDS_PT})

PALAVRAS_POR_TRECHO = 60
TAMANHO_RADICAL = 5  # radicalização leve: 'freático' e 'freáticos' viram 'freat'
STOPWORDS_CONSULTA = {"acontece", "qual", "quais", "como", "explica", "significa"}


def analisador(texto: str) -> list[str]:
    """Tokeniza, remove stopwords, reduz cada palavra ao radical e gera unigramas + bigramas."""
    vazias = set(STOPWORDS_NORM) | STOPWORDS_CONSULTA
    toks = [w[:TAMANHO_RADICAL] for w in re.findall(r"[a-z]+", normalizar(texto))
            if w not in vazias and len(w) > 1]
    return toks + [f"{a} {b}" for a, b in zip(toks, toks[1:])]


# ---------------------------------------------------------------- 1. ingestão --------------
def dividir_em_trechos(texto: str, alvo: int = PALAVRAS_POR_TRECHO) -> list[str]:
    paragrafos = [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip()]
    trechos, atual = [], []
    for p in paragrafos:
        palavras = p.split()
        if len(palavras) > alvo * 1.5:  # parágrafo longo: quebra por frases
            for frase in dividir_frases(p):
                atual.append(frase)
                if sum(len(x.split()) for x in atual) >= alvo:
                    trechos.append(" ".join(atual)); atual = []
            continue
        atual.append(p)
        if sum(len(x.split()) for x in atual) >= alvo:
            trechos.append("\n\n".join(atual)); atual = []
    if atual:
        trechos.append("\n\n".join(atual))
    return trechos


def dividir_frases(texto: str) -> list[str]:
    return [f.strip() for f in re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9])", texto) if f.strip()]


# ---------------------------------------------------------------- 2-3. índice e busca ------
@dataclass
class ResultadoBusca:
    trecho_id: int
    material_id: int
    texto: str
    similaridade: float


class IndiceSemantico:
    def __init__(self):
        self._vetorizador: TfidfVectorizer | None = None
        self._matriz = None
        self._meta: list[tuple[int, int, str]] = []

    def construir(self, trechos: list[tuple[int, int, str]]) -> None:
        """trechos = [(trecho_id, material_id, texto), ...]"""
        self._meta = trechos
        if not trechos:
            self._vetorizador, self._matriz = None, None
            return
        self._vetorizador = TfidfVectorizer(analyzer=analisador, sublinear_tf=True)
        self._matriz = self._vetorizador.fit_transform([t[2] for t in trechos])

    def buscar(self, consulta: str, k: int = 3, material_id: int | None = None,
               minimo: float = 0.05) -> list[ResultadoBusca]:
        if self._vetorizador is None or not consulta.strip():
            return []
        sims = cosine_similarity(self._vetorizador.transform([consulta]), self._matriz)[0]
        ordem = sims.argsort()[::-1]
        saida = []
        for i in ordem:
            tid, mid, texto = self._meta[i]
            if material_id is not None and mid != material_id:
                continue
            if sims[i] < minimo:
                break
            saida.append(ResultadoBusca(tid, mid, texto, float(sims[i])))
            if len(saida) == k:
                break
        return saida


indice = IndiceSemantico()


def reconstruir_indice(db) -> None:
    from .models import TrechoMaterial
    trechos = [(t.id, t.material_id, t.texto) for t in db.query(TrechoMaterial).all()]
    indice.construir(trechos)


# ---------------------------------------------------------------- 4. adaptação -------------
DESCRICAO_PERFIL = {
    "TDAH": "blocos curtos, resumo inicial em tópicos, termos-chave destacados e checklist",
    "TEA": "estrutura previsível (o que vou aprender → passo a passo → o que é importante), "
           "linguagem literal e direta",
    "DISLEXIA": "frases curtas, uma ideia por linha, espaçamento ampliado e sem itálico",
    "PADRAO": "texto original organizado em parágrafos",
}


_PALAVRA = r"[a-záéíóúâêôãõçà]+"
_IGNORAR = {normalizar(w) for w in """parte partes forma formas chamado chamada volta voltam
exemplo número números quantidade atitudes processo etapa etapas primeira segunda terceira
quarta outra outro existência superfície movimento necessária importante assim primeiro""".split()}


def termos_do_texto(texto: str, n: int = 6) -> list[str]:
    """Termos-chave na forma original (com acento): definições explícitas primeiro, depois frequência."""
    termos: list[str] = []

    def add(t):
        t = t.strip().lower()
        if len(t) > 3 and normalizar(t) not in _IGNORAR and normalizar(t) not in STOPWORDS_NORM \
                and normalizar(t) not in {normalizar(x) for x in termos}:
            termos.append(t)

    for m in re.finditer(rf"(?i)chamad[oa]s?\s+(?:de\s+)?({_PALAVRA}(?:\s+d[aoe]\s+{_PALAVRA})?)", texto):
        add(m.group(1))
    for m in re.finditer(rf"(?i)\b(?:é|são)\s+(?:o|a|os|as)\s+({_PALAVRA})(?=[.,;])", texto):
        add(m.group(1))
    contagem: dict[str, list] = {}
    for w in re.findall(_PALAVRA, texto.lower()):
        if len(w) >= 6:
            contagem.setdefault(normalizar(w), [w, 0])[1] += 1
    for _, (forma, qtd) in sorted(contagem.items(), key=lambda kv: -kv[1][1]):
        if qtd < 2:
            break
        add(forma)
    return termos[:n]


def _frases_curtas(texto: str, max_palavras: int = 18) -> list[str]:
    saida = []
    for frase in dividir_frases(texto.replace("\n", " ")):
        if len(frase.split()) <= max_palavras:
            saida.append(frase)
            continue
        # frase longa: quebra apenas em conectivos que iniciam uma nova ideia completa
        partes = re.split(r",\s+(?=(?:mas|porém|pois|porque)\b)|;\s+|,\s+e\s+(?=(?:o|a|os|as|parte|outra|outro)\b)", frase)
        for p in partes:
            p = p.strip().rstrip(",")
            if p:
                saida.append(p[0].upper() + p[1:] + ("" if p.endswith((".", "!", "?")) else "."))
    return saida


def _destacar(texto_html: str, termos: list[str]) -> str:
    for termo in termos:
        texto_html = re.sub(rf"(?i)(?<![\w>])({re.escape(termo)})(?![\w<])", r"<strong>\1</strong>",
                            texto_html, count=1)
    return texto_html


def _paragrafos(texto: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip()]


def adaptar_por_regras(titulo: str, texto: str, perfil: str, termos: list[str] | None = None) -> str:
    termos = termos if termos is not None else termos_do_texto(texto)
    paragrafos = _paragrafos(texto)

    if perfil == "TDAH":
        # resumo: a frase de abertura dos 3 parágrafos com mais termos-chave (em ordem original)
        aberturas = [(i, dividir_frases(p)[0]) for i, p in enumerate(paragrafos)]
        pontuar = lambda f: sum(normalizar(t) in normalizar(f) for t in termos)
        top = sorted(sorted(aberturas, key=lambda x: -pontuar(x[1]))[:3])
        partes = ['<section class="bloco destaque"><h3>Resumo rápido</h3><ul>'
                  + "".join(f"<li>{_destacar(html.escape(f), termos)}</li>" for _, f in top)
                  + "</ul></section>"]
        for n, p in enumerate(paragrafos, 1):
            titulo_bloco = next((t for t in termos if normalizar(t) in normalizar(p)), None)
            rotulo = f"{n}. {titulo_bloco.capitalize()}" if titulo_bloco else f"Parte {n}"
            frases = [_destacar(html.escape(f), termos) for f in _frases_curtas(p)]
            partes.append(f'<section class="bloco"><h3>{html.escape(rotulo)}</h3><p>'
                          + " ".join(frases) + "</p></section>")
        partes.append('<section class="bloco checklist"><h3>Checklist</h3><ul>'
                      + "".join(f'<li><label><input type="checkbox"> Sei explicar o que é '
                                f'<strong>{html.escape(t)}</strong></label></li>'
                                for t in termos[:4]) + "</ul></section>")
        return "\n".join(partes)

    if perfil == "TEA":
        passos = "".join(f"<li>{html.escape(f)}</li>" for f in _frases_curtas(texto))
        chave = "".join(f"<li><strong>{html.escape(t)}</strong></li>" for t in termos[:5])
        return (f'<section class="bloco"><h3>O que vou aprender</h3><p>Neste material você vai '
                f'aprender sobre: <strong>{html.escape(titulo)}</strong>. Ele tem '
                f'{len(paragrafos)} partes. Leia uma parte de cada vez.</p></section>'
                f'<section class="bloco"><h3>Passo a passo</h3><ol class="passos">{passos}</ol></section>'
                f'<section class="bloco destaque"><h3>Palavras importantes</h3><ul>{chave}</ul></section>'
                f'<section class="bloco"><h3>Quando terminar</h3><p>Volte para a lista de '
                f'materiais. Se tiver dúvida, use o campo “Perguntar sobre o material”.</p></section>')

    if perfil == "DISLEXIA":
        blocos = "".join('<div class="paragrafo">' + "".join(
            f'<p class="linha">{html.escape(f)}</p>' for f in _frases_curtas(p, 14)) + "</div>"
            for p in paragrafos)
        return f'<section class="bloco texto-dislexia">{blocos}</section>'

    return '<section class="bloco">' + "".join(f"<p>{html.escape(p)}</p>" for p in paragrafos) + "</section>"


def adaptar_com_llm(titulo: str, texto: str, perfil: str) -> str | None:
    """Gera a adaptação com um LLM, se houver chave configurada. Retorna None em caso de falha."""
    chave = os.getenv("ANTHROPIC_API_KEY")
    if not chave:
        return None
    try:
        import httpx
        prompt = (f"Você é um assistente pedagógico. Reescreva o material abaixo para um estudante "
                  f"com perfil {perfil}, usando: {DESCRICAO_PERFIL[perfil]}. Não invente "
                  f"informações que não estejam no texto. Responda apenas com HTML simples "
                  f"(section, h3, p, ul, ol, li, strong).\n\nTítulo: {titulo}\n\n{texto}")
        r = httpx.post("https://api.anthropic.com/v1/messages", timeout=60,
                       headers={"x-api-key": chave, "anthropic-version": "2023-06-01"},
                       json={"model": os.getenv("EDUMIND_LLM_MODELO", "claude-haiku-4-5-20251001"),
                             "max_tokens": 2000,
                             "messages": [{"role": "user", "content": prompt}]})
        r.raise_for_status()
        return r.json()["content"][0]["text"]
    except Exception:  # noqa: BLE001 — qualquer falha cai no adaptador por regras
        return None


def adaptar(titulo: str, texto: str, perfil: str) -> tuple[str, str]:
    """Retorna (html_adaptado, metodo)."""
    if perfil != "PADRAO":
        gerado = adaptar_com_llm(titulo, texto, perfil)
        if gerado:
            return gerado, "llm"
    return adaptar_por_regras(titulo, texto, perfil), "regras"


def responder_pergunta(pergunta: str, perfil: str, material_id: int | None = None):
    """Recupera trechos relevantes e devolve a resposta adaptada + métricas."""
    t0 = time.perf_counter()
    achados = indice.buscar(pergunta, k=2, material_id=material_id)
    t_busca = (time.perf_counter() - t0) * 1000
    if not achados:
        return None, [], t_busca
    contexto = "\n\n".join(a.texto for a in achados)
    html_resp, _ = adaptar("Resposta à sua pergunta", contexto, perfil)
    return html_resp, achados, t_busca
