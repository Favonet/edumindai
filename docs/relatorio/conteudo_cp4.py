"""Texto do CP4 (Relatório Final). Usa as funções de formatação de gerar_cp4.py."""


def escrever(g):
    P, B, H1, H2, Q, F, REF, DESTAQUE = (g[k] for k in ("P", "B", "H1", "H2", "Q", "F", "REF", "DESTAQUE"))
    corpo, runs, DIAG, TELAS = g["corpo"], g["runs"], g["DIAG"], g["TELAS"]

    def centro(texto, tam=24, sub=False, antes=240, depois=60):
        extra = '<w:u w:val="single"/>' if sub else ""
        corpo.append(f'<w:p><w:pPr><w:spacing w:before="{antes}" w:after="{depois}" w:line="276" w:lineRule="auto"/>'
                     f'<w:jc w:val="center"/></w:pPr>{runs("**" + texto + "**", tam=tam, extra=extra)}</w:p>')

    def rotulo(r, texto, italico=False, antes=120):
        corpo.append(f'<w:p><w:pPr><w:spacing w:before="{antes}" w:after="0" w:line="360" w:lineRule="auto"/>'
                     f'<w:jc w:val="both"/></w:pPr>{runs("**" + r + "** ")}{runs(texto, italico=italico)}</w:p>')

    # ------------------------------------------------------------------ título e resumo
    centro("EduMindAI – Plataforma de Ecossistema Educacional com Inteligência Artificial: "
           "Desenvolvimento e Validação do MVP")
    centro("Relatório Final – Projeto de Extensão Universitária - II", tam=22, sub=True, antes=60, depois=120)
    rotulo("Resumo:", "Este relatório final apresenta o resultado do projeto de extensão EduMindAI no semestre "
           "2026.2. O sistema foi entregue em duas releases, identificadas por versionamento semântico: a release "
           "0.1.0, descrita no relatório parcial, e a release 0.2.0, desenvolvida a partir dela e objeto principal "
           "deste documento. A release 0.2.0 trouxe busca híbrida no pipeline de Geração Aumentada de Recuperação "
           "(RAG), que combina embeddings do modelo multilíngue e5-small com o TF-IDF da versão anterior; cadastro "
           "de turmas e estudantes pela interface, com registro e revogação do consentimento do responsável; "
           "importação de materiais em PDF, DOCX e TXT; e uma segunda versão do classificador de sentimento. As "
           "duas releases foram comparadas com o mesmo protocolo: em 30 perguntas reservadas, que não foram usadas "
           "em nenhuma decisão de ajuste, a busca híbrida trouxe o trecho correto em primeiro lugar em 26 casos, "
           "contra 24 do TF-IDF, com percentil 95 do tempo de busca entre 157 e 248 ms (meta inferior a 500 ms). "
           "O sistema tem 53 testes automatizados aprovados e nenhuma violação automática das regras WCAG 2.1 A/AA "
           "nas 12 telas avaliadas. A validação com professores e estudantes, prevista no planejamento, não foi "
           "realizada, porque a parceria com uma escola da rede municipal não chegou a ser formalizada; o "
           "relatório registra essa limitação e propõe os passos para que ela ocorra.")
    rotulo("Palavras-Chave:", "Extensão Universitária, Inteligência Artificial, RAG, Embeddings, Neurodiversidade, "
           "Acessibilidade, LGPD, Release.", italico=True)

    # ------------------------------------------------------------------ I
    H1("I – Introdução / Justificativa")
    P("O modelo educacional padronizado impõe barreiras ao desenvolvimento de estudantes neurodivergentes, o "
      "que se traduz em lacunas de aprendizagem e evasão escolar. Segundo a Organização Mundial da Saúde, "
      "transtornos mentais afetam uma em cada oito pessoas no mundo (WHO, 2022). No Brasil, a Lei Brasileira de "
      "Inclusão (BRASIL, 2015) exige adaptações que garantam o acesso à educação, e a Lei Geral de Proteção de "
      "Dados Pessoais (BRASIL, 2018) impõe cuidado especial com dados de crianças e adolescentes. O EduMindAI se "
      "alinha à Agenda 2030 da ONU, em especial ao ODS 4 (Educação de Qualidade) e ao ODS 10 (Redução das "
      "Desigualdades) (ONU, 2015), ao apoiar o professor na adaptação de materiais e na percepção precoce de "
      "sinais de sofrimento emocional, tarefas que hoje dependem quase só do tempo disponível do docente.")
    P("A disciplina de Extensão Universitária II teve como foco transformar a modelagem feita em 2026.1 em um "
      "produto funcional. Na perspectiva de Freire (1980), a extensão é a construção conjunta de uma resposta a "
      "um problema concreto da comunidade, e não a entrega de um conhecimento pronto; um sistema executável é "
      "condição para esse diálogo com professores e estudantes. Por isso o desenvolvimento foi organizado em "
      "**releases**: versões completas e executáveis do sistema, identificadas por número de versão no "
      "formato MAIOR.MENOR.CORREÇÃO do versionamento semântico (PRESTON-WERNER, 2013). Cada release fecha uma "
      "iteração, fica marcada no histórico do repositório e pode ser instalada e comparada com as anteriores.")
    P("O relatório parcial (Checkpoint 3) descreveu a release 0.1.0, primeira versão de ponta a ponta do MVP. "
      "Este relatório final documenta a release 0.2.0, que melhora a anterior nos pontos que o próprio relatório "
      "parcial havia apontado como provisórios: a busca semântica, até então baseada apenas em TF-IDF; o "
      "cadastro de turmas e estudantes, que só podia ser feito por script; o registro do consentimento do "
      "responsável; e a classificação de sentimento. O documento também apresenta a comparação medida entre as "
      "duas releases e discute, com franqueza, o que não pôde ser feito, principalmente a validação com a "
      "comunidade escolar.")

    # ------------------------------------------------------------------ II
    H1("II – Objetivos (Geral e Específicos)")
    rotulo("Objetivo Geral:", "", antes=0)
    P("Desenvolver e validar um MVP da plataforma EduMindAI que adapte conteúdos didáticos e monitore "
      "indicadores socioemocionais de estudantes de Camboriú/SC, em conformidade com a WCAG 2.1 AA e a LGPD.")
    rotulo("Objetivos Específicos (com a situação final, em novembro de 2026):", "", antes=80)
    for t in (
        "a) Revisar e consolidar os artefatos de requisitos, modelagem e prototipação de 2026.1, ajustando o "
        "escopo ao que é exequível como MVP. **[Concluído]**",
        "b) Implementar o núcleo da aplicação, com autenticação e segregação de acessos por perfil (RF001), "
        "check-in emocional diário (RF003) e cadastro de turmas e estudantes pela interface (RF009). "
        "**[Concluído: releases 0.1.0 e 0.2.0]**",
        "c) Implementar o pipeline RAG para ingestão, indexação, recuperação e adaptação de materiais conforme o "
        "perfil do estudante (RF002), com importação de arquivos (RF010). **[Concluído: busca híbrida com "
        "embeddings na release 0.2.0]**",
        "d) Integrar a classificação de sentimento aos check-ins e disponibilizar o painel de alertas ao "
        "professor (RF004). **[Concluído com classificador léxico v2; modelo Transformer não implementado]**",
        "e) Realizar análise de segurança e adequação à LGPD (RNF001). **[Parcial: controles técnicos e "
        "registro do consentimento implementados; relatório de impacto (RIPD) não elaborado]**",
        "f) Verificar a acessibilidade (RNF002) e o desempenho da busca semântica (RNF003). **[Concluído na "
        "verificação automatizada; avaliação com usuários não realizada]**",
        "g) Conduzir a validação da solução com professores e estudantes. **[Não realizado: sem parceria "
        "formalizada com escola]**",
    ):
        P(t, recuo=False)

    # ------------------------------------------------------------------ III
    H1("III – Metodologia")
    P("O projeto manteve a abordagem híbrida descrita no relatório parcial: desenvolvimento iterativo e "
      "incremental do Processo Unificado (LARMAN, 2007), com ciclos curtos inspirados no Scrum (SCHWABER; "
      "SUTHERLAND, 2020), e documentação segundo o roteiro de análise e projeto orientados a objetos de "
      "Wazlawick (2011): casos de uso, diagramas de sequência do sistema (DSS), modelo de dados e contratos. "
      "O modelo de dados segue a progressão conceitual, lógica e física de Heuser (2009).")
    P("Cada iteração termina em uma release. O código é mantido em repositório Git, e cada release recebe uma "
      "marcação (tag) com seu número de versão: v0.1.0 ao fim da iteração 1 e v0.2.0 ao fim da iteração 2. As "
      "mudanças de cada versão ficam descritas em um arquivo de histórico (CHANGELOG). O número segue o "
      "versionamento semântico (PRESTON-WERNER, 2013): enquanto o número maior for zero, o sistema é "
      "considerado em desenvolvimento inicial; o aumento do número do meio indica novas funcionalidades "
      "compatíveis com a versão anterior. A release 0.2.0 cumpre essa compatibilidade: um banco de dados criado "
      "pela 0.1.0 é atualizado automaticamente na primeira execução, sem perda de dados.")
    P("Para comparar as releases de forma justa, a medição foi planejada antes das alterações. O gabarito de "
      "recuperação foi ampliado para 50 perguntas sobre cinco materiais e dividido em duas partes: 20 perguntas "
      "de **calibração**, usadas para escolher o modelo de embeddings e os pesos da busca, e 30 perguntas "
      "**reservadas**, usadas apenas uma vez, na medição final. Metade das perguntas reservadas usa as palavras "
      "do próprio texto, e a outra metade é parafraseada (por exemplo, \"por que chove?\" para um trecho que "
      "fala em condensação e precipitação). Para o sentimento, além das 20 frases do relatório parcial, foi "
      "escrita uma amostra nova de 40 frases. Há uma ressalva: essa amostra foi escrita depois de observar os "
      "erros da versão 1, e por isso pode favorecer a versão 2; o resultado na amostra antiga é a comparação "
      "mais confiável.")
    P("A verificação usou os mesmos instrumentos reprodutíveis do relatório parcial, todos no repositório: "
      "testes automatizados com pytest (SOMMERVILLE, 2011); varredura de acessibilidade com a biblioteca "
      "axe-core (DEQUE SYSTEMS, 2024) aplicando as regras WCAG 2.1 A e AA em navegador real; e um script que "
      "mede tempo de busca, acerto da recuperação e concordância do sentimento, salvando os números em arquivo. "
      "Os controles de segurança seguem o OWASP Top 10 (OWASP FOUNDATION, 2021). O sistema é executado "
      "localmente, em computador comum com Windows, por meio de um script de inicialização; não foi usada "
      "infraestrutura de nuvem nem contêineres. Todos os dados são fictícios.")

    # ------------------------------------------------------------------ IV
    H1("IV – Desenvolvimento")
    H2("a) Processo de Análise e Projeto de Sistemas")
    P("O planejamento previa três iterações (Quadro 1). As duas primeiras foram concluídas e geraram as "
      "releases 0.1.0 e 0.2.0. A terceira dependia da validação com uma escola parceira e não ocorreu. Dois "
      "itens planejados para a iteração 2 foram substituídos: o pgvector, porque o volume de dados de uma "
      "turma não justifica um servidor PostgreSQL dedicado nesta fase (os embeddings ficam gravados no próprio "
      "banco, em qualquer gerenciador); e o classificador BERTimbau, porque não havia dados reais rotulados "
      "para ajustá-lo e avaliá-lo de forma honesta.")
    Q("Planejamento e situação final das iterações do MVP.",
      ["Iteração", "Período", "Escopo", "Situação final"],
      [["1", "set.–out./2026", "Fluxos completos dos três perfis: login, check-in, alertas, materiais adaptados, "
        "perguntas (RAG com TF-IDF), indicadores, controles LGPD básicos.", "Concluída: **release 0.1.0**"],
       ["2", "out.–nov./2026", "Busca híbrida com embeddings; cadastro de turmas e estudantes; registro do "
        "consentimento; importação PDF/DOCX/TXT; sentimento v2.", "Concluída: **release 0.2.0**"],
       ["3", "nov.–dez./2026", "Ajustes a partir da validação com a escola parceira; relatório de segurança e "
        "LGPD.", "Não realizada (sem parceria)"]],
      [900, 1500, 4300, 2200])

    H2("b) Análise e Projeto de Sistemas de Informação Orientados a Objetos")
    P("A arquitetura em camadas foi mantida (Figura 1). A release 0.2.0 acrescentou dois elementos: o serviço de "
      "importação, que extrai o texto de arquivos enviados pelo professor, e o modelo de embeddings local, que "
      "transforma cada trecho do material em um vetor numérico. Esse modelo é opcional: se o pacote de IA não "
      "estiver instalado, a busca volta a usar apenas o TF-IDF, exatamente como na release 0.1.0. O serviço de "
      "segurança passou a registrar quem cadastrou o consentimento de cada estudante.")
    F(DIAG / "fig_arquitetura_v020.png", "Arquitetura em camadas da release 0.2.0.", largura_cm=13.5)
    P("O modelo de embeddings escolhido foi o multilingual-e5-small (WANG et al., 2024), da família de modelos "
      "de sentenças que aplica redes Transformer para produzir vetores comparáveis por similaridade de cosseno "
      "(REIMERS; GUREVYCH, 2019). Ele foi escolhido por ser multilíngue, pequeno (cerca de 470 MB) e executável "
      "em processador comum, sem placa de vídeo. O vetor de cada trecho é calculado uma única vez, no momento "
      "da publicação, e gravado no banco; na pergunta, só a frase do estudante precisa ser codificada. A "
      "pontuação final de cada trecho é 0,8 × similaridade dos embeddings + 0,2 × similaridade TF-IDF: o "
      "embedding reconhece paráfrases, e o TF-IDF mantém o peso de termos técnicos exatos.")

    H2("c) Requisitos (funcionais e não funcionais)")
    P("O Quadro 2 apresenta os requisitos e sua situação ao fim da release 0.2.0. Dois requisitos funcionais "
      "foram acrescentados (RF009 e RF010), ambos apontados no relatório parcial como necessários para que uma "
      "escola use o sistema sem a ajuda de um desenvolvedor.")
    Q("Requisitos do MVP e situação na release 0.2.0.",
      ["ID", "Descrição", "Prioridade", "Situação"],
      [["RF001", "Autenticar usuários e segregar o acesso por perfil (aluno, professor, gestor).", "Alta", "Implementado (0.1.0)"],
       ["RF002", "Adaptar materiais ao perfil sensorial (TDAH, TEA, dislexia) por meio de pipeline RAG.", "Alta",
        "Implementado; busca híbrida na 0.2.0"],
       ["RF003", "Registrar check-in emocional diário com escala visual e comentário opcional.", "Alta", "Implementado (0.1.0)"],
       ["RF004", "Classificar o sentimento dos check-ins e gerar alertas ao professor.", "Alta", "Implementado; v2 na 0.2.0"],
       ["RF005", "Publicar materiais e pré-visualizar cada versão adaptada.", "Alta", "Implementado (0.1.0)"],
       ["RF006", "Responder perguntas do estudante sobre o material, de forma adaptada.", "Média", "Implementado; híbrido na 0.2.0"],
       ["RF007", "Apresentar ao gestor indicadores agregados, sem identificar estudantes.", "Média", "Implementado (0.1.0)"],
       ["RF008", "Consultar a política de dados e exportar os próprios dados (LGPD, art. 18).", "Média", "Implementado (0.1.0)"],
       ["RF009", "Cadastrar turmas e estudantes e registrar/revogar o consentimento do responsável.", "Alta", "**Novo: implementado (0.2.0)**"],
       ["RF010", "Importar o texto de materiais em PDF, DOCX ou TXT (até 5 MB).", "Média", "**Novo: implementado (0.2.0)**"],
       ["RNF001", "Segurança e LGPD: hash de senhas, criptografia, auditoria, consentimento, retenção.", "Alta", "Parcial (sem RIPD)"],
       ["RNF002", "Acessibilidade WCAG 2.1 AA, alvos de toque de 44×44 px, leitores de tela.", "Alta", "Verificado (automático)"],
       ["RNF003", "Busca semântica com p95 inferior a 500 ms.", "Média", "Atendido (157–248 ms)"]],
      [900, 4700, 1100, 2200])

    H2("d) Casos de Uso de Alto Nível")
    P("A Figura 2 mostra o diagrama de casos de uso da release 0.2.0; os três casos novos estão destacados em "
      "amarelo e descritos no Quadro 3. Os casos UC01 a UC10 permanecem como no relatório parcial, e o UC04 "
      "passou a usar a busca híbrida.")
    F(DIAG / "fig_casos_de_uso_v020.png", "Diagrama de casos de uso da release 0.2.0 (novos em amarelo).", largura_cm=15.5)
    Q("Casos de uso acrescentados na release 0.2.0.",
      ["Caso de uso", "Ator", "Descrição"],
      [["UC11 Gerenciar turmas e estudantes", "Professor", "Cria turmas, cadastra estudantes com perfil de "
        "leitura e recebe a senha provisória, exibida uma única vez; altera o perfil quando necessário."],
       ["UC12 Registrar/revogar consentimento do responsável", "Professor", "Informa o nome do responsável, a "
        "data do termo e confirma que o termo assinado está arquivado; pode revogar a qualquer momento."],
       ["UC13 Importar arquivo", "Professor", "Envia um PDF, DOCX ou TXT; o sistema extrai o texto e segue o "
        "fluxo de publicação (UC05)."]],
      [2700, 1300, 4900])

    H2("e) Casos de Uso Expandidos")
    P("O UC12 é o caso novo mais sensível, pois trata da base legal para o tratamento de dados de menores (LGPD, "
      "art. 14). O sistema não substitui o termo em papel; ele registra que o termo existe, quem o registrou e "
      "quando, e bloqueia o check-in emocional enquanto não houver consentimento.")
    Q("Caso de uso expandido UC12 – Registrar consentimento do responsável.",
      ["Item", "Descrição"],
      [["Ator principal", "Professor"],
       ["Pré-condições", "Professor autenticado; estudante cadastrado em uma turma do próprio professor."],
       ["Fluxo principal", "1. O professor abre \"Turmas e alunos\".\n2. O sistema lista os estudantes e a "
        "situação do consentimento.\n3. O professor escolhe \"Registrar termo\" para um estudante.\n4. Informa "
        "o nome do responsável, a data de assinatura e marca que o termo assinado está arquivado na escola.\n"
        "5. O sistema valida os dados, grava o consentimento, o responsável e o autor do registro, e anota a "
        "ação na trilha de auditoria.\n6. O check-in emocional fica liberado para o estudante."],
       ["Fluxos alternativos", "4a. Data futura ou confirmação desmarcada: o sistema recusa e mostra a mensagem "
        "de erro.\n3a. Revogação: o professor escolhe \"Revogar\"; o sistema remove o consentimento, registra na "
        "auditoria e bloqueia novos check-ins."],
       ["Pós-condições", "Consentimento registrado com responsável, data e autor; ação auditada."],
       ["Regras", "Somente o professor da turma acessa o estudante (outro professor recebe \"não encontrado\")."]],
      [2000, 6900])
    P("O UC04 (Perguntar sobre o material) manteve o fluxo do relatório parcial, com uma mudança no passo de "
      "recuperação: a pergunta é convertida em vetor pelo modelo e5-small, comparada com os vetores dos "
      "trechos gravados no banco e combinada com a pontuação TF-IDF. A resposta passou a informar o modo de "
      "busca usado (híbrida ou TF-IDF), para que o funcionamento fique transparente.")

    H2("f) Diagramas de Sequência do Sistema (DSS)")
    P("As Figuras 3 e 4 mostram as operações de sistema dos dois fluxos principais da release 0.2.0.")
    F(DIAG / "fig_dss_consentimento.png", "DSS do cadastro de estudante e registro do consentimento (UC11 e UC12).", largura_cm=14)
    F(DIAG / "fig_dss_pergunta.png", "DSS da pergunta sobre o material com busca híbrida (UC04).", largura_cm=14)

    H2("g) Modelo Conceitual, Lógico e Físico do Banco de Dados")
    P("O modelo lógico (Figura 5) manteve as entidades da release 0.1.0 e acrescentou cinco colunas, marcadas "
      "como novas. O Quadro 5 descreve essas colunas no modelo físico. Elas são criadas automaticamente em um "
      "banco da versão anterior por uma rotina de migração executada na inicialização.")
    F(DIAG / "fig_modelo_logico_v020.png", "Modelo lógico da release 0.2.0.", largura_cm=16, altura_max_cm=18)
    Q("Colunas acrescentadas no modelo físico da release 0.2.0.",
      ["Tabela.coluna", "Tipo", "Finalidade"],
      [["trecho_material.embedding", "BLOB / BYTEA", "Vetor de 384 números (float32) do trecho, calculado uma vez."],
       ["trecho_material.embedding_modelo", "VARCHAR(120)", "Nome do modelo que gerou o vetor; se mudar, o vetor é recalculado."],
       ["estudante.nome_responsavel", "VARCHAR(120)", "Responsável que assinou o termo de consentimento."],
       ["estudante.consentimento_registrado_por", "INTEGER", "Usuário (professor) que registrou o termo."],
       ["material.origem", "VARCHAR(160)", "Nome do arquivo importado, ou texto digitado."]],
      [3300, 1600, 4000])

    H2("h) Contratos das operações de sistema")
    Q("Contratos das principais operações de sistema da release 0.2.0.",
      ["Operação", "Pré-condições", "Pós-condições"],
      [["cadastrarEstudante(nome, email, turma, perfil)", "Professor autenticado e dono da turma; e-mail não "
        "cadastrado.", "Usuário e Estudante criados; senha provisória gerada e exibida uma vez, guardada apenas "
        "como hash; ação auditada."],
       ["registrarConsentimento(estudante, responsável, data, arquivado)", "Estudante da turma do professor; data "
        "não futura; termo arquivado confirmado.", "consentimento = verdadeiro; responsável, data e autor "
        "gravados; ação auditada."],
       ["importarMaterial(turma, arquivo)", "Arquivo PDF, DOCX ou TXT de até 5 MB, com texto extraível.",
        "Material criado com origem; trechos, vetores e adaptações gerados."],
       ["perguntar(material, pergunta)", "Estudante autenticado da turma do material.", "Resposta adaptada ao "
        "perfil com os 2 trechos de maior pontuação; modo de busca informado."]],
      [2700, 2900, 3300])

    H2("i) Tecnologias e telas da release 0.2.0")
    Q("Tecnologias utilizadas.",
      ["Camada", "Tecnologia", "Uso no projeto"],
      [["Back-end", "Python 3, FastAPI, Jinja2", "Rotas, regras de negócio e páginas renderizadas no servidor"],
       ["Persistência", "SQLAlchemy 2, SQLite (PostgreSQL opcional)", "Banco de dados e migração de colunas"],
       ["IA", "scikit-learn (TF-IDF), sentence-transformers (e5-small)", "Busca híbrida e embeddings locais"],
       ["Importação", "pypdf, python-docx", "Extração de texto de PDF e DOCX"],
       ["Segurança", "cryptography (Fernet), PBKDF2, CSRF", "Criptografia, hash de senhas e proteção de formulários"],
       ["Qualidade", "pytest, Playwright, axe-core", "Testes, capturas de tela e acessibilidade"],
       ["Versionamento", "Git (tags v0.1.0 e v0.2.0), CHANGELOG", "Controle de releases"]],
      [1700, 3400, 3800])
    P("As Figuras 6 a 10 mostram as telas novas da release 0.2.0. As telas da release 0.1.0 (login, check-in, "
      "materiais adaptados, alertas e indicadores) continuam válidas e estão no relatório parcial.")
    F(TELAS / "14_prof_turmas.png", "Tela \"Turmas e alunos\": criação de turma e cadastro de estudante.", largura_cm=14)
    F(TELAS / "15_prof_cadastro_senha.png", "Senha provisória exibida uma única vez após o cadastro.", largura_cm=14)
    F(TELAS / "16_prof_registro_termo.png", "Registro do termo de consentimento do responsável.", largura_cm=8)
    F(TELAS / "10_prof_materiais.png", "Publicação de material com envio de arquivo (PDF, DOCX ou TXT).", largura_cm=14)
    F(TELAS / "17_pergunta_parafrase_hibrida.png", "Pergunta parafraseada (\"por que chove?\") respondida pela "
      "busca híbrida.", largura_cm=13)

    # ------------------------------------------------------------------ V
    H1("V – Resultados Alcançados")
    P("O resultado principal do projeto é o sistema EduMindAI na release 0.2.0, funcional e executável em um "
      "computador da escola. Ele cobre os quatro requisitos funcionais originais e os seis derivados, atende aos "
      "três perfis de usuário e tem documentação de instalação e uso. O Quadro 8 reúne os indicadores medidos "
      "nas duas releases com o mesmo script e os mesmos dados.")
    Q("Indicadores medidos nas releases 0.1.0 e 0.2.0.",
      ["Indicador", "Release 0.1.0", "Release 0.2.0", "Meta"],
      [["Recuperação: trecho certo em 1º lugar (30 perguntas reservadas)", "24/30 (80%)", "**26/30 (87%)**", "–"],
       ["Recuperação: trecho certo entre os 3 primeiros", "28/30", "**29/30**", "–"],
       ["Recuperação: perguntas parafraseadas, 1º lugar", "11/15", "**12/15**", "–"],
       ["Tempo de busca p95, 5 materiais (14 trechos)", "10 ms", "157 ms", "< 500 ms"],
       ["Tempo de busca p95, 100 materiais (280 trechos)", "10 ms", "248 ms", "< 500 ms"],
       ["Sentimento: amostra do relatório parcial (20 frases)", "17/20", "17/20", "–"],
       ["Sentimento: amostra nova (40 frases)", "32/40", "**40/40***", "–"],
       ["Testes automatizados aprovados", "29", "**53**", "todos"],
       ["Violações WCAG 2.1 A/AA (axe-core)", "0 em 10 telas", "0 em 12 telas", "0"]],
      [4300, 1500, 1500, 1600])
    corpo.append('<w:p><w:pPr><w:spacing w:before="0" w:after="120" w:line="240" w:lineRule="auto"/></w:pPr>'
                 + runs("* Amostra escrita após conhecer os erros da versão 1; ver discussão.", tam=16) + "</w:p>")
    P("As Figuras 11 e 12 mostram o sistema em uso nos outros dois contextos previstos: o check-in do "
      "estudante no celular, com a escala de humor em botões grandes, e o painel de indicadores do gestor, "
      "que apresenta adesão, sentimento médio e alertas por turma sem identificar estudantes.")
    F(TELAS / "12_mobile_checkin.png", "Interface para dispositivo móvel: check-in emocional do estudante.",
      largura_cm=6.5, altura_max_cm=13)
    F(TELAS / "11_gestor.png", "Painel do gestor para avaliação e acompanhamento das ações.", largura_cm=14,
      altura_max_cm=14)
    P("A Figura 13 resume a comparação entre as duas releases.")
    F(DIAG / "fig_comparacao_releases.png", "Comparação entre as releases 0.1.0 e 0.2.0.", largura_cm=15)
    P("Quanto ao público-alvo, é preciso ser claro: **não houve interação com a comunidade externa** durante o "
      "semestre. Não foi possível formalizar a parceria com uma escola da rede municipal de Camboriú, e por isso "
      "nenhum professor, estudante ou responsável usou o sistema, e não há dados de usabilidade, de satisfação "
      "ou de impacto pedagógico. Os resultados acima são exclusivamente técnicos, obtidos com dados fictícios. "
      "O que o projeto entrega à comunidade, neste momento, é um sistema pronto para ser testado, com dados de "
      "demonstração, documentação e um protocolo de medição reprodutível.")

    # ------------------------------------------------------------------ VI
    H1("VI – Discussões")
    P("**Ganho da busca híbrida.** A melhora foi real, mas modesta: duas perguntas a mais em 30 no primeiro "
      "lugar e uma a mais entre os três primeiros. Com 30 perguntas, essa diferença não permite afirmar com "
      "segurança estatística que a busca híbrida é superior; o resultado indica uma tendência favorável, "
      "concentrada nas perguntas com palavras diferentes das do texto, que é exatamente o caso que o TF-IDF não "
      "resolve. Em troca, o tempo de busca subiu de cerca de 10 ms para 157 a 248 ms, ainda abaixo da meta de "
      "500 ms, e a indexação de 100 materiais levou cerca de 50 segundos, feita uma única vez. Para uma turma, "
      "esse custo é aceitável.")
    P("**O primeiro modelo testado não serviu.** O primeiro modelo de embeddings avaliado (paraphrase-"
      "multilingual-MiniLM) não superou o TF-IDF nas perguntas reservadas (23 contra 24). O modelo e5-small foi "
      "escolhido usando apenas as perguntas de calibração, e só depois foi medido nas reservadas. Registrar esse "
      "insucesso é importante: trocar uma técnica simples por uma rede neural não garante melhora, e só a "
      "medição com dados separados permitiu perceber isso.")
    P("**Limitação descoberta.** No e5-small, as similaridades ficam comprimidas numa faixa estreita: perguntas "
      "sem relação com o material ainda obtêm cerca de 0,66, e perguntas relacionadas, a partir de 0,68. Com "
      "isso, não foi possível definir um limite confiável para o sistema responder \"não encontrei isso no "
      "material\"; ele sempre devolve os trechos mais próximos. Esse é o principal ponto a resolver antes do uso "
      "real, pois uma resposta fora de contexto pode confundir um estudante neurodivergente.")
    P("**Sentimento.** Na amostra do relatório parcial as duas versões acertaram 17 de 20; os três erros "
      "restantes (\"não gostei da prova mas tudo bem\", \"foi legal\" e \"tô de boa\") são frases cujo rótulo "
      "correto é discutível. Na amostra nova, a versão 2 acertou 40 de 40, contra 32 da versão 1, mas, como essa "
      "amostra foi escrita depois de conhecer os erros da versão 1, o número superestima a melhora. A conclusão "
      "honesta é que a versão 2 trata melhor contraste (\"mas\"), atenuação e negação, sem piorar o que já "
      "funcionava. Um classificador como o BERTimbau (SOUZA; NOGUEIRA; LOTUFO, 2020) só faz sentido com frases "
      "reais de estudantes, rotuladas por profissionais da escola.")
    P("**Mudanças de escopo.** Duas tecnologias planejadas no relatório parcial foram deixadas de lado com "
      "justificativa: o pgvector, desnecessário para o volume de uma turma, já que os vetores ficam no próprio "
      "banco; e a implantação em contêiner, substituída por execução local com um script de inicialização, mais "
      "simples para uma escola sem equipe de TI. O sistema continua compatível com PostgreSQL, mas essa "
      "configuração não foi testada nesta release.")
    Q("Atendimento dos objetivos específicos.",
      ["Objetivo", "Situação", "Evidência"],
      [["a) Revisar artefatos", "Atendido", "Seção IV; relatório parcial"],
       ["b) Núcleo da aplicação", "Atendido", "Releases 0.1.0 e 0.2.0; testes de integração"],
       ["c) Pipeline RAG", "Atendido", "Busca híbrida; 26/30 nas perguntas reservadas"],
       ["d) Sentimento e alertas", "Parcial", "Léxico v2; Transformer não implementado"],
       ["e) Segurança e LGPD", "Parcial", "Consentimento, auditoria, criptografia; sem RIPD"],
       ["f) Acessibilidade e desempenho", "Atendido (automático)", "0 violações axe; p95 < 500 ms"],
       ["g) Validação com usuários", "Não atendido", "Sem parceria com escola"]],
      [2900, 2000, 4000])
    P("**Reflexão sobre a aprendizagem.** O projeto ensinou que medir é tão importante quanto construir. "
      "Separar perguntas de calibração e de avaliação, registrar o modelo que não funcionou e admitir a "
      "contaminação da amostra de sentimento foram decisões que tornaram os resultados mais confiáveis, ainda "
      "que menos impressionantes. Também ficou claro que a parte mais difícil de um projeto de extensão não é "
      "técnica: sem a articulação institucional com a escola, o sistema não chega ao público para o qual foi "
      "feito. Essa etapa deveria ter começado junto com o desenvolvimento, e não depois dele.")

    # ------------------------------------------------------------------ VII
    H1("VII – Conclusões e Recomendações Futuras")
    P("O projeto entregou um MVP funcional da plataforma EduMindAI em duas releases. A release 0.2.0 tornou o "
      "sistema utilizável por uma escola sem apoio técnico, com cadastro de turmas e estudantes, registro do "
      "consentimento dos responsáveis e importação de arquivos, e melhorou, de forma medida, a busca semântica "
      "e a análise de sentimento. Os requisitos não funcionais de acessibilidade e desempenho foram atendidos "
      "na verificação automatizada. O objetivo de validação com a comunidade não foi alcançado, e por isso o "
      "projeto termina como um produto pronto para ser testado, e não como uma solução validada.")
    P("Para a continuidade do projeto, recomenda-se:", recuo=True)
    for t in ("formalizar a parceria com uma escola da rede municipal de Camboriú, com termo de cooperação e "
              "apresentação à equipe pedagógica;",
              "realizar sessões de validação com professores e, após o consentimento dos responsáveis, com "
              "estudantes, usando roteiros de tarefas e questionário de usabilidade;",
              "elaborar o Relatório de Impacto à Proteção de Dados (RIPD) antes de qualquer uso com dados reais;",
              "resolver a resposta para perguntas fora do material, com um limite calibrado ou um segundo modelo "
              "de reordenação;",
              "avaliar um classificador Transformer em português com frases reais rotuladas pela escola;",
              "instalar o sistema em um servidor da escola ou do IFC com HTTPS e cópias de segurança;",
              "caso se use um modelo de linguagem externo, definir salvaguardas para que nenhum dado pessoal seja "
              "enviado a terceiros."):
        B(t)

    # ------------------------------------------------------------------ VIII
    H1("VIII – Referências Bibliográficas")
    for r in (
        "ALVES, William P. **Projetos de sistemas web**: conceitos, estruturas, criação de banco de dados e "
        "ferramentas de desenvolvimento. São Paulo: Érica, 2015.",
        "BRASIL. Lei nº 13.146, de 6 de julho de 2015. Lei Brasileira de Inclusão da Pessoa com Deficiência. "
        "Disponível em: http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm. Acesso em: 5 out. 2026.",
        "BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD). "
        "Disponível em: http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm. Acesso em: 5 out. 2026.",
        "DEQUE SYSTEMS. **axe-core**: accessibility engine for automated web UI testing. Disponível em: "
        "https://github.com/dequelabs/axe-core. Acesso em: 5 out. 2026.",
        "FREIRE, Paulo. **Extensão ou comunicação?** 5. ed. Rio de Janeiro: Paz e Terra, 1980.",
        "HEUSER, Carlos Alberto. **Projeto de banco de dados**. 6. ed. Porto Alegre: Bookman, 2009.",
        "INSTITUTO FEDERAL CATARINENSE. Biblioteca. **Normas para elaboração de trabalhos acadêmicos**. "
        "Disponível em: https://biblioteca.ifc.edu.br/trabalho-academico/. Acesso em: 5 out. 2026.",
        "LARMAN, Craig. **Utilizando UML e padrões**: uma introdução à análise e ao projeto orientados a objetos "
        "e ao desenvolvimento iterativo. 3. ed. Porto Alegre: Bookman, 2007.",
        "LEWIS, Patrick et al. Retrieval-augmented generation for knowledge-intensive NLP tasks. **Advances in "
        "Neural Information Processing Systems**, v. 33, p. 9459-9474, 2020.",
        "ORGANIZAÇÃO DAS NAÇÕES UNIDAS. **Transformando nosso mundo**: a Agenda 2030 para o desenvolvimento "
        "sustentável. Nova Iorque: ONU, 2015.",
        "OWASP FOUNDATION. **OWASP Top 10**: the ten most critical web application security risks. 2021. "
        "Disponível em: https://owasp.org/www-project-top-ten/. Acesso em: 5 out. 2026.",
        "PRESTON-WERNER, Tom. **Semantic Versioning 2.0.0**. 2013. Disponível em: https://semver.org/lang/pt-BR/. "
        "Acesso em: 20 out. 2026.",
        "REIMERS, Nils; GUREVYCH, Iryna. Sentence-BERT: sentence embeddings using siamese BERT-networks. In: "
        "CONFERENCE ON EMPIRICAL METHODS IN NATURAL LANGUAGE PROCESSING (EMNLP-IJCNLP), 2019, Hong Kong. "
        "**Proceedings** [...]. Hong Kong: ACL, 2019. p. 3982-3992.",
        "SALTON, Gerard; BUCKLEY, Christopher. Term-weighting approaches in automatic text retrieval. "
        "**Information Processing & Management**, v. 24, n. 5, p. 513-523, 1988.",
        "SCHWABER, Ken; SUTHERLAND, Jeff. **O Guia do Scrum**: o guia definitivo para o Scrum. 2020. "
        "Disponível em: https://scrumguides.org. Acesso em: 5 out. 2026.",
        "SOMMERVILLE, Ian. **Engenharia de software**. 9. ed. São Paulo: Pearson Prentice Hall, 2011.",
        "SOUZA, Fábio; NOGUEIRA, Rodrigo; LOTUFO, Roberto. BERTimbau: pretrained BERT models for Brazilian "
        "Portuguese. In: BRAZILIAN CONFERENCE ON INTELLIGENT SYSTEMS (BRACIS), 9., 2020. **Proceedings** [...]. "
        "Cham: Springer, 2020. p. 403-417.",
        "WANG, Liang et al. **Multilingual E5 text embeddings**: a technical report. arXiv:2402.05672, 2024. "
        "Disponível em: https://arxiv.org/abs/2402.05672. Acesso em: 20 out. 2026.",
        "WAZLAWICK, Raul Sidnei. **Análise e projeto de sistemas de informação orientados a objetos**. 2. ed. "
        "Rio de Janeiro: Elsevier, 2011.",
        "WORLD HEALTH ORGANIZATION. **World mental health report**: transforming mental health for all. "
        "Geneva: WHO, 2022.",
        "WORLD WIDE WEB CONSORTIUM. **Web Content Accessibility Guidelines (WCAG) 2.1**. Disponível em: "
        "https://www.w3.org/TR/WCAG21/. Acesso em: 5 out. 2026.",
    ):
        REF(r)

    # ------------------------------------------------------------------ Apêndices
    H1("Apêndices")
    H2("Apêndice A – Cronograma final (agosto a dezembro de 2026)")
    Q("Cronograma de execução e situação final.",
      ["Etapa", "Ago.", "Set.", "Out.", "Nov.", "Dez.", "Situação final"],
      [["1 – Revisão do material e definição do escopo do MVP", "X", "X", "", "", "", "Concluída"],
       ["2 – Desenvolvimento da solução", "", "X", "X", "X", "", "Concluída (releases 0.1.0 e 0.2.0)"],
       ["3 – Análise de segurança e conformidade com a LGPD", "", "", "X", "X", "", "Parcial (sem RIPD)"],
       ["4 – Articulação institucional com a rede municipal", "", "", "X", "X", "", "Não concluída"],
       ["5 – Validação da solução com os usuários", "", "", "", "X", "X", "Não realizada"],
       ["6 – Consolidação da documentação e apresentação final", "", "", "", "X", "", "Concluída"]],
      [3500, 600, 600, 600, 600, 600, 2400])
    H2("Apêndice B – Fotos e demais registros das ações de extensão")
    P("Não houve encontros com a comunidade externa durante o semestre, e por isso não há fotos ou atas de "
      "reuniões. Os registros do trabalho realizado são o histórico do repositório (com as releases marcadas), "
      "as capturas de tela das Figuras 6 a 12 e do relatório parcial, o resultado da verificação de "
      "acessibilidade e o arquivo de medições usado no Quadro 8.")
    H2("Apêndice C – Como executar e usuários de demonstração")
    P("No Windows, com Python instalado, basta executar o arquivo iniciar.bat na pasta do projeto: ele instala "
      "as dependências, cria o banco de demonstração e abre o sistema em http://localhost:8000. Todos os "
      "usuários fictícios usam a senha edumind123: professor@escola.demo (professor), gestora@escola.demo "
      "(gestora), ana@escola.demo (aluna com perfil TDAH), bruno@escola.demo (aluno com perfil TEA) e "
      "carla@escola.demo (aluna com perfil dislexia).")

    # ------------------------------------------------------------------ Anexos
    H1("Anexos")
    P("**Anexo A – Código-fonte da release 0.2.0 (Google Drive):** "
      "https://drive.google.com/file/d/1lpdqY5p4nO7sRYosHtaqYY8aMTycOKnd/view?usp=sharing. O arquivo contém o "
      "código, os 53 testes automatizados, o script de medição dos indicadores do Quadro 8, o script de captura "
      "de telas e verificação de acessibilidade, o histórico de versões (CHANGELOG) e as instruções de execução "
      "(README). O histórico completo, com as releases marcadas como v0.1.0 e v0.2.0, é mantido em repositório "
      "Git.", recuo=False)
    P("**Anexo B – Agenda 2030 da ONU (ODS 4 e ODS 10):** "
      "https://brasil.un.org/pt-br/91863-agenda-2030-para-o-desenvolvimento-sustentavel", recuo=False)
    P("**Anexo C – Diretrizes WCAG 2.1 (W3C):** https://www.w3.org/TR/WCAG21/", recuo=False)
    P("**Anexo D – Lei Geral de Proteção de Dados:** "
      "http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm", recuo=False)
