"""Gera os indicadores da release 0.2.0 usados no relatório final (CP4):
  - desempenho da busca (RNF003): TF-IDF e híbrida, com 5 materiais e com ~500 trechos;
  - acerto da recuperação (RF002): gabarito de 50 perguntas (20 de calibração, 30 de avaliação);
  - classificador de sentimento (RF004): v1 (v0.1.0) × v2 (v0.2.0) nas duas amostras.

Uso: python tests/medir_desempenho.py   (precisa do pacote sentence-transformers para a busca híbrida)
"""
import json
import logging
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
logging.disable(logging.WARNING)
from app import rag  # noqa: E402
from app.seed import MATERIAIS  # noqa: E402
from app.sentimento import analisar as analisar_v2  # noqa: E402
from tests.amostra_sentimento import AMOSTRA_CP3, AMOSTRA_NOVA  # noqa: E402
from tests.gabarito import AVALIACAO, CALIBRACAO  # noqa: E402
from tests.referencia_sentimento_v010 import analisar as analisar_v1  # noqa: E402

CONSULTAS = ["o que é condensação", "como somar frações", "por que chove",
             "qual é o maior planeta", "por que as folhas são verdes"]


def _trechos(materiais):
    saida = []
    for mid, (_, _, txt) in enumerate(materiais):
        saida += [(len(saida) + i, mid, t) for i, t in enumerate(rag.dividir_em_trechos(txt))]
    return saida


def _indice(trechos, com_emb):
    ind = rag.IndiceSemantico()
    t0 = time.perf_counter()
    emb = rag.codificador.codificar([t[2] for t in trechos]) if com_emb else None
    ind.construir(trechos, emb)
    return ind, (time.perf_counter() - t0) * 1000


def _tempos(ind, modo, repeticoes=20):
    ind.buscar(CONSULTAS[0], modo=modo)  # aquecimento
    tempos = []
    for q in CONSULTAS * repeticoes:
        t0 = time.perf_counter(); ind.buscar(q, modo=modo); tempos.append((time.perf_counter() - t0) * 1000)
    return {"media_ms": round(statistics.mean(tempos), 2),
            "p95_ms": round(statistics.quantiles(tempos, n=20)[18], 2)}


def _acerto(ind, perguntas, modo):
    t1 = sum(1 for q, e, *_ in perguntas if (r := ind.buscar(q, k=1, modo=modo, minimo=-1)) and e in r[0].texto)
    t3 = sum(1 for q, e, *_ in perguntas
             if any(e in x.texto for x in ind.buscar(q, k=3, modo=modo, minimo=-1)))
    return {"perguntas": len(perguntas), "top1": t1, "top3": t3}


def _sentimento(fn, amostra):
    erros = [(h, t, e, fn(h, t).rotulo) for h, t, e in amostra if fn(h, t).rotulo != e]
    return {"amostra": len(amostra), "acertos": len(amostra) - len(erros), "erros": erros}


def medir():
    com_emb = rag.codificador.disponivel()
    saida = {"modelo_embeddings": rag.codificador.nome if com_emb else None,
             "peso_embeddings": rag.PESO_EMBEDDINGS, "busca": {}}

    for rotulo, mats in (("5 materiais", MATERIAIS), ("100 materiais", MATERIAIS * 20)):
        trechos = _trechos(mats)
        ind, ms_idx = _indice(trechos, com_emb)
        saida["busca"][rotulo] = {"trechos": len(trechos), "indexacao_ms": round(ms_idx, 1),
                                  "tfidf": _tempos(ind, "tfidf")}
        if com_emb:
            saida["busca"][rotulo]["hibrida"] = _tempos(ind, "auto")

    ind, _ = _indice(_trechos(MATERIAIS), com_emb)
    saida["recuperacao"] = {}
    for nome, conj in (("calibracao", CALIBRACAO), ("avaliacao", AVALIACAO)):
        r = {"tfidf": _acerto(ind, conj, "tfidf")}
        if com_emb:
            r["hibrida"] = _acerto(ind, conj, "auto")
            for tipo in ("literal", "parafrase"):
                sub = [p for p in conj if p[2] == tipo]
                r[f"tfidf_{tipo}"] = _acerto(ind, sub, "tfidf")
                r[f"hibrida_{tipo}"] = _acerto(ind, sub, "auto")
        saida["recuperacao"][nome] = r

    saida["sentimento"] = {
        "v1_cp3": _sentimento(analisar_v1, AMOSTRA_CP3), "v2_cp3": _sentimento(analisar_v2, AMOSTRA_CP3),
        "v1_nova": _sentimento(analisar_v1, AMOSTRA_NOVA), "v2_nova": _sentimento(analisar_v2, AMOSTRA_NOVA)}
    return saida


if __name__ == "__main__":
    print(json.dumps(medir(), indent=2, ensure_ascii=False))
