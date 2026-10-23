"""Gera as métricas do relatório parcial: desempenho da busca (RNF003), acerto da
recuperação (RF002) e concordância do classificador de sentimento (RF004).

Uso: python tests/medir_desempenho.py
"""
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import rag  # noqa: E402
from app.seed import MATERIAIS  # noqa: E402
from app.sentimento import analisar  # noqa: E402

CONSULTAS = ["o que é condensação", "como somar frações", "lençol freático",
             "numerador e denominador", "evaporação das plantas"]

PERGUNTAS_GABARITO = [  # (pergunta, trecho que deve aparecer no 1º resultado)
    ("o que é condensação?", "condensação"), ("o que acontece na evaporação", "evaporação"),
    ("o que é precipitação", "precipitação"), ("o que é lençol freático", "freáticos"),
    ("por que o ciclo da água é importante", "importante porque"),
    ("o que é o denominador", "denominador indica"),
    ("o que são frações equivalentes", "equivalentes são"),
    ("como somar frações com mesmo denominador", "somar frações"),
    ("o que é transpiração das plantas", "transpiração"), ("o que é o numerador", "numerador indica"),
]

AMOSTRA_SENTIMENTO = [  # (humor, comentário, rótulo esperado — anotado manualmente)
    (5, "muito feliz hoje!", "positivo"), (4, "gostei da aula", "positivo"), (4, "", "positivo"),
    (3, "normal", "neutro"), (3, "dormi pouco", "neutro"), (2, "estou cansada e triste", "negativo"),
    (1, "", "negativo"), (3, "não estou bem hoje", "negativo"),
    (4, "não gostei da prova mas tudo bem", "neutro"), (2, "brigaram comigo no ônibus", "negativo"),
    (5, "joguei bola com meus amigos", "positivo"), (3, "fiquei confuso na aula", "negativo"),
    (4, "aprendi frações", "positivo"), (2, "", "negativo"), (3, "foi legal", "neutro"),
    (1, "não aguento mais", "negativo"), (4, "estou com sono", "neutro"), (5, "", "positivo"),
    (3, "meu cachorro ficou doente", "negativo"), (2, "tô de boa", "negativo"),
]


def medir():
    saida = {"busca": {}}
    for n in (2, 50, 200):
        trechos = []
        for mid, (_, _, txt) in enumerate((MATERIAIS * 100)[:n]):
            trechos += [(len(trechos) + i, mid, t) for i, t in enumerate(rag.dividir_em_trechos(txt))]
        ind = rag.IndiceSemantico()
        t0 = time.perf_counter(); ind.construir(trechos); t_idx = (time.perf_counter() - t0) * 1000
        tempos = []
        for q in CONSULTAS * 40:
            t0 = time.perf_counter(); ind.buscar(q); tempos.append((time.perf_counter() - t0) * 1000)
        saida["busca"][n] = {"trechos": len(trechos), "indexacao_ms": round(t_idx, 1),
                             "media_ms": round(statistics.mean(tempos), 2),
                             "p95_ms": round(statistics.quantiles(tempos, n=20)[18], 2)}

    ind = rag.IndiceSemantico(); trechos = []
    for mid, (_, _, txt) in enumerate(MATERIAIS):
        trechos += [(len(trechos) + i, mid, t) for i, t in enumerate(rag.dividir_em_trechos(txt))]
    ind.construir(trechos)
    top1 = sum(1 for q, e in PERGUNTAS_GABARITO if (r := ind.buscar(q, k=1)) and e in r[0].texto)
    top3 = sum(1 for q, e in PERGUNTAS_GABARITO if any(e in x.texto for x in ind.buscar(q, k=3)))
    saida["recuperacao"] = {"perguntas": len(PERGUNTAS_GABARITO), "acerto_top1": top1, "acerto_top3": top3}

    erros = [(h, t, e, analisar(h, t).rotulo) for h, t, e in AMOSTRA_SENTIMENTO if analisar(h, t).rotulo != e]
    saida["sentimento"] = {"amostra": len(AMOSTRA_SENTIMENTO),
                           "acertos": len(AMOSTRA_SENTIMENTO) - len(erros), "erros": erros}
    return saida


if __name__ == "__main__":
    print(json.dumps(medir(), indent=2, ensure_ascii=False))
