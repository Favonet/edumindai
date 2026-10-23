"""Captura as telas do MVP e roda a verificação automática de acessibilidade (axe-core, WCAG 2.1 AA).

Uso: com o servidor rodando em localhost:8000 e o banco de demonstração criado,
    python tests/capturar_telas.py <pasta_saida> <caminho_axe.min.js>
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://localhost:8000"
SAIDA = Path(sys.argv[1]); SAIDA.mkdir(parents=True, exist_ok=True)
AXE = Path(sys.argv[2]).read_text()
resultados = {}


def axe(page, nome):
    page.add_script_tag(content=AXE)
    r = page.evaluate("""async () => { const r = await axe.run(document, {runOnly: {type: 'tag',
        values: ['wcag2a','wcag2aa','wcag21a','wcag21aa']}}); return {violacoes: r.violations.map(v =>
        ({id: v.id, impacto: v.impact, nos: v.nodes.length, descricao: v.help})), aprovadas: r.passes.length}; }""")
    resultados[nome] = r


def login(page, email):
    page.goto(f"{BASE}/login")
    page.fill("#email", email); page.fill("#senha", "edumind123")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")


def sair(page):
    page.click("text=Sair")


with sync_playwright() as p:
    nav = p.chromium.launch()
    page = nav.new_page(viewport={"width": 1280, "height": 860}, device_scale_factor=1.5, bypass_csp=True)

    page.goto(f"{BASE}/login"); axe(page, "login")
    page.screenshot(path=SAIDA / "01_login.png")

    # Aluna com TDAH: check-in
    login(page, "ana@escola.demo")
    page.check("input[name=humor][value='4']")
    page.fill("#comentario", "gostei da aula de ciências, aprendi bastante")
    axe(page, "aluno_checkin")
    page.screenshot(path=SAIDA / "02_aluno_checkin.png", full_page=True)
    page.click("button.grande"); page.wait_for_load_state("networkidle")
    page.screenshot(path=SAIDA / "03_aluno_checkin_enviado.png", full_page=True)
    page.click("text=Meus materiais"); page.click("text=O ciclo da água")
    axe(page, "aluno_material_tdah")
    page.screenshot(path=SAIDA / "04_material_tdah.png", full_page=True)
    page.fill("#pergunta", "o que acontece na condensação?")
    page.click("text=Perguntar >> nth=-1"); page.wait_for_load_state("networkidle")
    page.locator(".resposta").scroll_into_view_if_needed()
    page.screenshot(path=SAIDA / "05_pergunta_rag.png", full_page=True)
    sair(page)

    # Aluno com TEA e aluna com dislexia: mesmo material
    login(page, "bruno@escola.demo"); page.goto(f"{BASE}/aluno/materiais/1")
    axe(page, "aluno_material_tea")
    page.screenshot(path=SAIDA / "06_material_tea.png", full_page=True); sair(page)
    login(page, "carla@escola.demo"); page.goto(f"{BASE}/aluno/materiais/1")
    page.screenshot(path=SAIDA / "07_material_dislexia.png", full_page=True); sair(page)

    # Professor
    login(page, "professor@escola.demo")
    axe(page, "prof_painel")
    page.screenshot(path=SAIDA / "08_prof_painel.png", full_page=True)
    page.click("nav >> text=Alertas"); axe(page, "prof_alertas")
    page.screenshot(path=SAIDA / "09_prof_alertas.png", full_page=True)
    page.click("nav >> text=Materiais"); axe(page, "prof_materiais")
    page.screenshot(path=SAIDA / "10_prof_materiais.png", full_page=True)
    # v0.2.0: turmas e alunos (RF009)
    page.click("nav >> text=Turmas e alunos"); page.wait_for_load_state("networkidle")
    axe(page, "prof_turmas")
    page.screenshot(path=SAIDA / "14_prof_turmas.png", full_page=True)
    page.fill("#nome-aluno", "Isabela Nunes"); page.fill("#email-aluno", "isabela@escola.demo")
    page.select_option("#perfil-novo", "DISLEXIA")
    page.click("section[aria-labelledby=novo-aluno] button[type=submit]")
    page.wait_for_load_state("networkidle")
    axe(page, "prof_turmas_cadastro")
    page.screenshot(path=SAIDA / "15_prof_cadastro_senha.png", full_page=False)
    page.locator("tr", has_text="Isabela Nunes").locator("summary").click()
    page.locator("tr", has_text="Isabela Nunes").scroll_into_view_if_needed()
    page.screenshot(path=SAIDA / "16_prof_registro_termo.png", full_page=False)
    sair(page)

    # v0.2.0: pergunta parafraseada respondida pela busca híbrida (RF002)
    login(page, "ana@escola.demo"); page.goto(f"{BASE}/aluno/materiais/1")
    page.fill("#pergunta", "por que chove?")
    page.click("text=Perguntar >> nth=-1"); page.wait_for_load_state("networkidle")
    page.locator("section", has=page.locator("#pergunta")).screenshot(
        path=SAIDA / "17_pergunta_parafrase_hibrida.png")
    sair(page)

    # Gestora
    login(page, "gestora@escola.demo"); axe(page, "gestor")
    page.screenshot(path=SAIDA / "11_gestor.png", full_page=True); sair(page)

    # Celular (Figura 2 do modelo: interface para dispositivo móvel)
    cel = nav.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, bypass_csp=True)
    login(cel, "eduarda@escola.demo")
    cel.check("input[name=humor][value='3']")
    axe(cel, "aluno_checkin_mobile")
    cel.screenshot(path=SAIDA / "12_mobile_checkin.png", full_page=True)

    # Alto contraste + letra maior
    cel.click("summary"); cel.check("input[name=alto_contraste]"); cel.check("input[name=fonte_grande]")
    cel.click(".prefs button"); cel.wait_for_load_state("networkidle")
    axe(cel, "aluno_alto_contraste")
    cel.screenshot(path=SAIDA / "13_mobile_alto_contraste.png", full_page=False)
    nav.close()

(SAIDA / "axe_resultados.json").write_text(json.dumps(resultados, indent=2, ensure_ascii=False))
for nome, r in resultados.items():
    print(f"{nome:24s} violações={len(r['violacoes'])} regras_aprovadas={r['aprovadas']} {r['violacoes']}")
