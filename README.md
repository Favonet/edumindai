# EduMindAI — versão 0.2.0

Plataforma educacional com IA para apoiar estudantes neurodivergentes (TEA, TDAH e dislexia), professores e gestores da rede municipal de Camboriú/SC.
Projeto de Extensão Universitária II — BSI / IFC Camboriú (2026.2). Histórico de versões em [CHANGELOG.md](CHANGELOG.md).

## O que o sistema faz

| Requisito | Funcionalidade |
|---|---|
| RF001 | Login com perfis **aluno**, **professor** e **gestor**; cada perfil só acessa suas telas |
| RF002 | Professor publica o material → o sistema divide em trechos, indexa e gera versões adaptadas para TDAH, TEA e dislexia; o aluno pergunta sobre o material e a resposta vem da **busca híbrida** (embeddings + TF-IDF) |
| RF003 | Check-in emocional diário do aluno (5 opções + comentário opcional) |
| RF004 | Sentimento do check-in (v2) e alertas ao professor (risco imediato e tendência negativa) |
| RF005–RF008 | Publicação e pré-visualização de materiais, perguntas ao material, indicadores do gestor, direitos do titular |
| **RF009** (0.2.0) | Professor cria turmas, cadastra estudantes, muda o perfil de leitura e registra/revoga o consentimento do responsável |
| **RF010** (0.2.0) | Importação de materiais em PDF, DOCX e TXT |
| RNF001 | Senhas com PBKDF2, comentários criptografados, CSRF, bloqueio de login, cabeçalhos de segurança, auditoria, exportação de dados, retenção |
| RNF002 | Telas acessíveis (WCAG 2.1 AA verificada com axe-core), alvos de 44 px, alto contraste, letra maior |
| RNF003 | Busca com p95 abaixo de 500 ms |

## Como rodar (Windows)

Dê dois cliques em **`iniciar.bat`**. Na primeira vez ele cria o ambiente Python, instala as dependências (inclui o pacote de IA; o modelo de ~470 MB é baixado no primeiro uso) e cria um banco com dados **fictícios**. Depois abra http://localhost:8000.

Para apresentar em outro aparelho na mesma rede Wi-Fi, use `http://IP-DO-PC:8000` (o IP aparece com `ipconfig`).

Todos os usuários de demonstração usam a senha `edumind123`:

- `professor@escola.demo`: turma, alertas, materiais e cadastro de alunos
- `gestora@escola.demo`: indicadores agregados e auditoria
- `ana@escola.demo` (TDAH), `bruno@escola.demo` (TEA) e `carla@escola.demo` (dislexia): alunos

### Manualmente

```bash
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements-ia.txt   # ou requirements.txt, sem a busca por embeddings
python -m app.seed                   # recria o banco com dados de demonstração
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Testes e medições

```bash
python -m pytest -q                  # 53 testes automatizados
python tests/medir_desempenho.py     # indicadores do relatório final (docs/medidas_v0.2.0.json)
python tests/capturar_telas.py telas/ caminho/para/axe.min.js   # capturas + verificação WCAG
```

## Configuração (variáveis de ambiente, todas opcionais)

| Variável | Para quê |
|---|---|
| `EDUMIND_EMBEDDINGS=0` | Desliga a busca por embeddings (usa só TF-IDF) |
| `EDUMIND_MODELO_EMBEDDINGS` | Troca o modelo (padrão `intfloat/multilingual-e5-small`) |
| `EDUMIND_PESO_EMBEDDINGS` | Peso dos embeddings na busca híbrida (padrão 0,8) |
| `DATABASE_URL` | Banco. Padrão: SQLite (`edumindai.db`). PostgreSQL: instale `psycopg[binary]` e use `postgresql+psycopg://usuario:senha@host/edumindai` |
| `EDUMIND_SEGREDO_SESSAO` | Segredo do cookie de sessão (sem ele, as sessões caem a cada reinício) |
| `EDUMIND_CHAVE_DADOS` | Chave Fernet dos comentários. Sem ela, é gerada no arquivo `.chave_dados` |
| `EDUMIND_HTTPS=1` | Cookie seguro, quando atrás de HTTPS |
| `ANTHROPIC_API_KEY` | Opcional: adaptações geradas por modelo de linguagem; sem ela, o adaptador por regras funciona offline |

## Estrutura

```
app/
  main.py        rotas web (controladores)
  models.py      modelo de dados (SQLAlchemy)
  db.py          conexão e migração das colunas novas
  rag.py         RAG: trechos, embeddings, busca híbrida, adaptação por perfil
  sentimento.py  classificador de sentimento (v2)
  alertas.py     regras dos alertas preditivos
  importacao.py  leitura de PDF, DOCX e TXT
  seguranca.py   hash de senha, criptografia, CSRF, auditoria
  retencao.py    política de retenção (LGPD)
  seed.py        dados fictícios de demonstração
tests/           testes, gabarito de 50 perguntas, amostras de sentimento e scripts de medição
docs/            medições da release
```

## Próximos passos

1. Validação com professores e estudantes de uma escola parceira (ainda não realizada).
2. Classificador Transformer (BERTimbau) ajustado com dados reais anonimizados.
3. Implantação em servidor com HTTPS e PostgreSQL.
