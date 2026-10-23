# EduMindAI — MVP

Plataforma educacional com IA para apoiar estudantes neurodivergentes (TEA, TDAH e dislexia), professores e gestores da rede municipal de Camboriú/SC.
Projeto de Extensão Universitária II — BSI / IFC Camboriú (2026.2).

## O que já funciona (iteração 1)

| Requisito | Funcionalidade |
|---|---|
| RF001 | Login com perfis **aluno**, **professor** e **gestor**; cada perfil só acessa suas telas |
| RF002 | Professor publica o texto da aula → o sistema divide em trechos, indexa e gera versões adaptadas para TDAH, TEA e dislexia; o aluno pode fazer perguntas sobre o material (busca semântica / RAG) |
| RF003 | Check-in emocional diário do aluno (5 opções com emoji + comentário opcional) |
| RF004 | Análise de sentimento do check-in e alertas para o professor (risco imediato e tendência negativa), com registro do acompanhamento |
| RNF001 | Senhas com PBKDF2, comentários criptografados no banco, proteção CSRF, bloqueio após 5 tentativas de login, cabeçalhos de segurança, trilha de auditoria, exportação dos dados do titular, rotina de retenção |
| RNF002 | Telas sem violações automáticas WCAG 2.1 AA (axe-core), alvos de 44 px, navegação por teclado, letra maior, alto contraste e espaçamento ampliado |
| RNF003 | Busca semântica com p95 abaixo de 2 ms para 500 trechos (meta: 500 ms) |

## Como rodar

Precisa do Python 3.11 ou mais novo.

```bash
python -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app.seed               # cria o banco com dados FICTÍCIOS de demonstração
uvicorn app.main:app --reload
```

Abra http://localhost:8000. Todos os usuários de demonstração usam a senha `edumind123`:

- `professor@escola.demo`: painel da turma, alertas e materiais
- `gestora@escola.demo`: indicadores agregados e auditoria
- `ana@escola.demo` (TDAH), `bruno@escola.demo` (TEA) e `carla@escola.demo` (dislexia): alunos

## Testes e métricas

```bash
python -m pytest -q                  # 29 testes automatizados
python tests/medir_desempenho.py     # métricas usadas no relatório parcial
# capturas de tela + verificação de acessibilidade (precisa de Playwright e axe-core):
python tests/capturar_telas.py telas/ caminho/para/axe.min.js
```

## Configuração (variáveis de ambiente)

| Variável | Para quê |
|---|---|
| `DATABASE_URL` | Banco. Padrão: SQLite local. Para PostgreSQL: `postgresql+psycopg://usuario:senha@host/edumindai` |
| `EDUMIND_SEGREDO_SESSAO` | Segredo do cookie de sessão (defina em produção) |
| `EDUMIND_CHAVE_DADOS` | Chave Fernet para criptografar os comentários. Se não definir, é gerada no arquivo `.chave_dados` |
| `EDUMIND_HTTPS=1` | Marca o cookie como seguro (use atrás de HTTPS) |
| `ANTHROPIC_API_KEY` | Opcional. Se definida, as adaptações passam a ser geradas por um modelo de linguagem; sem ela o sistema usa o adaptador por regras, que funciona offline |

## Estrutura

```
app/
  main.py        rotas web (controladores)
  models.py      modelo de dados (SQLAlchemy)
  rag.py         pipeline RAG: trechos, índice, busca, adaptação por perfil
  sentimento.py  classificador de sentimento (léxico + escala de humor)
  alertas.py     regras dos alertas preditivos
  seguranca.py   hash de senha, criptografia, CSRF, auditoria
  retencao.py    política de retenção (LGPD)
  seed.py        dados fictícios de demonstração
  templates/     telas (Jinja2)
  static/        CSS
tests/           testes automatizados e scripts de medição
```

## Próximas iterações

1. Trocar o TF-IDF por embeddings no PostgreSQL + pgvector.
2. Trocar o classificador por léxico por um modelo Transformer em português (BERTimbau).
3. Cadastro de turmas e alunos pela interface, além da importação de PDF/DOCX.
4. Implantar em homologação e validar com a escola parceira.
