"""Testes de unidade: segurança, sentimento e RAG."""
import statistics
import time

from app import rag, seguranca
from app.sentimento import analisar, polaridade_texto


# ---- Segurança (RNF001) ----
def test_hash_de_senha_verifica_e_nao_guarda_texto_puro():
    h = seguranca.gerar_hash_senha("segredo123")
    assert "segredo123" not in h
    assert seguranca.verificar_senha("segredo123", h)
    assert not seguranca.verificar_senha("errada", h)


def test_hash_com_sal_diferente_a_cada_vez():
    assert seguranca.gerar_hash_senha("x") != seguranca.gerar_hash_senha("x")


def test_criptografia_do_comentario_e_reversivel():
    c = seguranca.cifrar("me senti sozinho")
    assert "sozinho" not in c
    assert seguranca.decifrar(c) == "me senti sozinho"


# ---- Sentimento (RF004) ----
def test_humor_alto_sem_texto_e_positivo():
    assert analisar(5).rotulo == "positivo"


def test_humor_baixo_e_negativo():
    assert analisar(1, "").rotulo == "negativo"


def test_negacao_inverte_polaridade():
    assert polaridade_texto("estou bem") > 0
    assert polaridade_texto("não estou bem") < 0


def test_texto_negativo_puxa_humor_neutro_para_baixo():
    r = analisar(3, "estou triste e cansada")
    assert r.score < 0


def test_expressao_de_risco_sempre_gera_negativo_e_sinal():
    r = analisar(4, "Não aguento mais isso")
    assert r.sinal_risco and r.rotulo == "negativo"


# ---- RAG (RF002 / RNF003) ----
TEXTO = """A fotossíntese é o processo em que as plantas produzem o próprio alimento usando a luz do Sol.

A clorofila é o pigmento verde que absorve a luz. Ela fica dentro dos cloroplastos, nas folhas.

Na respiração celular, a planta consome oxigênio e libera gás carbônico, de dia e de noite."""


def test_divisao_em_trechos_preserva_todo_o_texto():
    trechos = rag.dividir_em_trechos(TEXTO, alvo=15)
    assert len(trechos) >= 2
    assert "clorofila" in " ".join(trechos)


def test_busca_recupera_trecho_correto():
    ind = rag.IndiceSemantico()
    ind.construir([(i, 1, t) for i, t in enumerate(rag.dividir_em_trechos(TEXTO, alvo=15))])
    r = ind.buscar("o que é a clorofila?", k=1)
    assert r and "clorofila" in r[0].texto


def test_busca_sem_relacao_nao_retorna_nada():
    ind = rag.IndiceSemantico()
    ind.construir([(0, 1, TEXTO)])
    assert ind.buscar("campeonato de futebol") == []


def test_adaptacoes_por_perfil_tem_estrutura_propria():
    tdah = rag.adaptar_por_regras("Plantas", TEXTO, "TDAH")
    tea = rag.adaptar_por_regras("Plantas", TEXTO, "TEA")
    dis = rag.adaptar_por_regras("Plantas", TEXTO, "DISLEXIA")
    assert "Resumo rápido" in tdah and "Checklist" in tdah
    assert "Passo a passo" in tea and "<ol" in tea
    assert 'class="linha"' in dis and "<em>" not in dis


def test_adaptacao_escapa_html_malicioso():
    html_ = rag.adaptar_por_regras("x", "<script>alert(1)</script> " + TEXTO, "DISLEXIA")
    assert "<script>" not in html_


def test_desempenho_da_busca_p95_abaixo_de_500ms():
    from app.seed import MATERIAIS
    trechos = []
    for mid, (_, _, txt) in enumerate(MATERIAIS * 25):  # ~50 materiais
        trechos += [(len(trechos) + i, mid, t) for i, t in enumerate(rag.dividir_em_trechos(txt))]
    ind = rag.IndiceSemantico(); ind.construir(trechos)
    tempos = []
    for q in ["o que é condensação", "como somar frações", "lençol freático", "numerador"] * 25:
        t0 = time.perf_counter(); ind.buscar(q); tempos.append((time.perf_counter() - t0) * 1000)
    p95 = statistics.quantiles(tempos, n=20)[18]
    assert p95 < 500
