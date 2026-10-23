"""Gera as figuras de modelagem da release 0.2.0 (usadas no relatório final / CP4).

Desenha diagramas Graphviz (DOT, via viz.js) e Mermaid num Chromium sem janela (Playwright)
e salva em PNG nesta pasta. Precisa de internet na primeira execução (bibliotecas via CDN).
Uso: python docs/diagramas/gerar_diagramas.py
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

PASTA = Path(__file__).parent
VIZ = "https://cdn.jsdelivr.net/npm/@viz-js/viz@3.11.0/lib/viz-standalone.js"
MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"

ESTILO_DOT = ('fontname="Arial"; node [fontname="Arial", fontsize=13, shape=box, '
              'style="rounded,filled", fillcolor="#ffffff", color="#4f5d68"]; '
              'edge [fontname="Arial", fontsize=11, color="#4f5d68"];')

ARQUITETURA = """digraph G { rankdir=TB; nodesep=0.35; ranksep=0.45; %s
  nav [label="Navegador (computador, tablet ou celular)\\nHTML semântico + CSS acessível", fillcolor="#f5f4f0"];
  subgraph cluster_app { label="Aplicação EduMindAI 0.2.0 (Python / FastAPI) — execução local"; fontsize=15;
    color="#1f6f68"; style=rounded;
    apres [label="Camada de apresentação\\nRotas FastAPI + templates Jinja2\\n(controle de acesso por perfil, CSRF)"];
    subgraph cluster_serv { label="Serviços"; style="rounded,dashed"; color="#888888"; fontsize=14;
      sent [label="Sentimento v2\\n+ regras de alerta", fillcolor="#e3efed"];
      seg [label="Segurança e LGPD\\nhash, criptografia, auditoria,\\nconsentimento do responsável", fillcolor="#e3efed"];
      rag [label="Pipeline RAG\\ntrechos → índice híbrido → busca\\n→ adaptação por perfil", fillcolor="#e3efed"];
      imp [label="Importação\\nPDF, DOCX e TXT", fillcolor="#e3efed"];
    }
    emb [label="Modelo de embeddings local\\nmultilingual-e5-small\\n(opcional; sem ele: só TF-IDF)", fillcolor="#fcf1d8", style="rounded,filled,dashed"];
    pers [label="Camada de persistência\\nSQLAlchemy (ORM) + migração de colunas"];
  }
  llm [label="LLM externo (opcional)\\nadaptação generativa", fillcolor="#fcf1d8", style="rounded,filled,dashed"];
  db [label="Banco de dados\\nSQLite (local)\\nPostgreSQL (opcional)", shape=cylinder, fillcolor="#f5f4f0"];
  nav -> apres [label=" HTTP / HTTPS"];
  apres -> sent; apres -> seg; apres -> rag; apres -> imp;
  rag -> emb [style=dashed, label=" vetores"];
  imp -> rag [label=" texto extraído"];
  sent -> pers; seg -> pers; rag -> pers;
  rag -> llm [style=dashed, label=" se houver chave"];
  pers -> db;
}""" % ESTILO_DOT

CASOS_DE_USO = """digraph G { rankdir=LR; nodesep=0.25; ranksep=1.2; %s
  node [shape=box, style="rounded", fillcolor="#ffffff"];
  aluno [label="«ator»\\nAluno"]; prof [label="«ator»\\nProfessor"]; gestor [label="«ator»\\nGestor"];
  usuario [label="«ator»\\nUsuário", style="rounded,dashed"];
  subgraph cluster_s { label="EduMindAI 0.2.0"; fontsize=16; color="#1f6f68"; style=rounded;
    node [shape=ellipse, style=filled, fillcolor="#e3efed", color="#1f6f68"];
    uc04 [label="UC04 Perguntar sobre\\no material (busca híbrida)"]; uc10 [label="UC10 Configurar\\npreferências de leitura"];
    uc02 [label="UC02 Registrar check-in\\nemocional"]; uc03 [label="UC03 Consultar material\\nadaptado"];
    uc07 [label="UC07 Tratar alerta"]; uc05 [label="UC05 Publicar material\\ndidático"];
    uc13 [label="UC13 Importar arquivo\\n(PDF, DOCX, TXT)", fillcolor="#fcf1d8"];
    uc06 [label="UC06 Acompanhar turma"];
    uc11 [label="UC11 Gerenciar turmas\\ne estudantes", fillcolor="#fcf1d8"];
    uc12 [label="UC12 Registrar/revogar consentimento\\ndo responsável", fillcolor="#fcf1d8"];
    uc01 [label="UC01 Autenticar-se"]; uc09 [label="UC09 Exercer direitos do\\ntitular (exportar dados)"];
    uc08 [label="UC08 Consultar indicadores\\ne auditoria"];
  }
  aluno -> {uc04 uc10 uc02 uc03} [arrowhead=none];
  prof -> {uc07 uc05 uc06 uc11 uc12} [arrowhead=none];
  gestor -> uc08 [arrowhead=none];
  usuario -> {uc01 uc09} [arrowhead=none];
  uc13 -> uc05 [style=dashed, label="«extend»"];
  uc04 -> uc03 [style=dashed, label="«extend»"];
  {aluno prof gestor} -> usuario [arrowhead=empty, color="#888888"];
}""" % ESTILO_DOT

DSS_CONSENTIMENTO = """sequenceDiagram
  actor P as :Professor
  participant S as :Sistema
  P->>S: abrirTurmas()
  S-->>P: estudantes da turma e situação do consentimento
  P->>S: cadastrarEstudante(nome, email, turma, perfil)
  S-->>P: senha provisória (exibida uma única vez)
  P->>S: registrarConsentimento(estudante, nomeResponsavel, dataTermo, termoArquivado)
  Note right of S: valida data e confirmação,<br/>grava responsável e auditoria
  S-->>P: consentimento registrado (check-in liberado)
"""

DSS_PERGUNTA = """sequenceDiagram
  actor A as :Aluno
  participant S as :Sistema
  A->>S: abrirMaterial(material)
  S-->>A: material adaptado ao perfil
  A->>S: perguntar(material, pergunta)
  Note right of S: embedding da pergunta (e5-small)<br/>+ TF-IDF → 2 trechos mais similares<br/>(só TF-IDF se o modelo faltar)
  S-->>A: resposta adaptada, trechos usados e modo da busca
"""

MODELO_LOGICO = """erDiagram
  USUARIO ||--o| ESTUDANTE : "é"
  USUARIO ||--o{ TURMA : "leciona"
  TURMA ||--o{ ESTUDANTE : "tem"
  ESTUDANTE ||--o{ CHECKIN : "registra"
  ESTUDANTE ||--o{ ALERTA : "recebe"
  CHECKIN |o--o{ ALERTA : "origina"
  TURMA ||--o{ MATERIAL : "recebe"
  MATERIAL ||--|{ TRECHO_MATERIAL : "dividido em"
  MATERIAL ||--o{ ADAPTACAO : "adaptado em"
  USUARIO |o--o{ LOG_ACESSO : "gera"
  USUARIO { int id PK
    string email UK
    string senha_hash
    string perfil }
  ESTUDANTE { int id PK
    int usuario_id FK
    int turma_id FK
    string perfil_sensorial
    bool consentimento_responsavel
    date data_consentimento
    string nome_responsavel "novo 0.2.0"
    int consentimento_registrado_por "novo 0.2.0" }
  TURMA { int id PK
    int professor_id FK
    string nome
    string escola }
  CHECKIN { int id PK
    int estudante_id FK
    date data
    int humor
    text comentario_cifrado
    float sentimento_score }
  ALERTA { int id PK
    int estudante_id FK
    int checkin_id FK
    string nivel
    string status }
  MATERIAL { int id PK
    int turma_id FK
    text texto_original
    string origem "novo 0.2.0" }
  TRECHO_MATERIAL { int id PK
    int material_id FK
    text texto
    blob embedding "novo 0.2.0"
    string embedding_modelo "novo 0.2.0" }
  ADAPTACAO { int id PK
    int material_id FK
    string perfil_sensorial
    text conteudo_html }
  LOG_ACESSO { int id PK
    int usuario_id FK
    string acao
    datetime data_hora }
"""

PAGINA = """<!doctype html><html><head><meta charset="utf-8">
<style>body{margin:0;background:#fff;font-family:Arial,sans-serif} #alvo{display:inline-block;padding:16px}</style>
<script src="%s"></script><script src="%s"></script></head><body><div id="alvo"></div></body></html>""" % (VIZ, MERMAID)


def gerar():
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pg = nav.new_page(device_scale_factor=2, viewport={"width": 1600, "height": 1200})
        pg.set_content(PAGINA, wait_until="networkidle")
        pg.evaluate("""() => mermaid.initialize({startOnLoad: false, theme: 'base', themeVariables: {
            primaryColor: '#e3efed', primaryBorderColor: '#1f6f68', primaryTextColor: '#111',
            noteBkgColor: '#fcf1d8', noteBorderColor: '#8a5a00', lineColor: '#333',
            fontFamily: 'Arial', fontSize: '18px'}, sequence: {useMaxWidth: false, actorFontSize: 18, messageFontSize: 18, noteFontSize: 17, width: 180}, er: {useMaxWidth: false, fontSize: 15}})""")
        for nome, dot in (("fig_arquitetura_v020", ARQUITETURA), ("fig_casos_de_uso_v020", CASOS_DE_USO)):
            pg.evaluate("""async (dot) => { const viz = await Viz.instance();
                const svg = viz.renderSVGElement(dot); const a = document.getElementById('alvo');
                a.innerHTML = ''; a.appendChild(svg); }""", dot)
            pg.locator("#alvo").screenshot(path=PASTA / f"{nome}.png")
        for nome, mmd in (("fig_dss_consentimento", DSS_CONSENTIMENTO), ("fig_dss_pergunta", DSS_PERGUNTA),
                          ("fig_modelo_logico_v020", MODELO_LOGICO)):
            pg.evaluate("""async (codigo) => { const {svg} = await mermaid.render('d' + Date.now(), codigo);
                document.getElementById('alvo').innerHTML = svg; }""", mmd)
            pg.locator("#alvo").screenshot(path=PASTA / f"{nome}.png")
        nav.close()


if __name__ == "__main__":
    gerar()
    print("Diagramas gerados em", PASTA)
