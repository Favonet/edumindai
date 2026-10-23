# Histórico de versões

O projeto segue versionamento semântico. Cada release corresponde a uma iteração do
Projeto de Extensão Universitária II (BSI / IFC Camboriú).

## [0.2.0] — outubro de 2026 (iteração 2, relatório final / CP4)

### Novo
- **Busca híbrida no RAG (RF002):** o modelo multilíngue `intfloat/multilingual-e5-small`
  gera um embedding para cada trecho, gravado no banco; a busca combina a similaridade dos
  embeddings (peso 0,8) com a do TF-IDF (peso 0,2). Sem o pacote de IA o sistema usa só o
  TF-IDF, como na 0.1.0. O modo da busca aparece para o estudante e em `/saude`.
- **Cadastro de turmas e estudantes pela interface (RF009):** o professor cria turmas,
  cadastra estudantes (senha provisória exibida uma única vez), altera o perfil de leitura
  e registra o termo de consentimento do responsável (nome, data e confirmação de que o
  termo assinado está arquivado), com revogação.
- **Importação de materiais (RF010):** PDF, DOCX e TXT de até 5 MB, com limpeza de quebras
  de linha e aviso quando o PDF não tem texto (imagem escaneada).
- **Sentimento v2 (RF004):** contraste ("mas" pesa a parte final), atenuadores ("meio",
  "um pouco"), negação de palavra negativa como positivo fraco, expressões de várias
  palavras e léxico ampliado. A detecção de expressões de risco não mudou.
- Versão do sistema no rodapé e em `/saude`; script `iniciar.bat` para rodar no Windows.

### Medições (tests/medir_desempenho.py, docs/medidas_v0.2.0.json)
- Recuperação, 30 perguntas reservadas: 1º resultado 26/30 (TF-IDF: 24/30); top-3 29/30 (28/30).
- Tempo da busca híbrida: p95 de 157 a 248 ms (meta < 500 ms); TF-IDF ~10 ms.
- Sentimento: amostra nova de 40 frases 40/40 (v1: 32/40); amostra do CP3 17/20 nas duas versões.

### Alterado
- Banco: colunas `trecho_material.embedding`, `trecho_material.embedding_modelo`,
  `estudante.nome_responsavel`, `estudante.consentimento_registrado_por`, `material.origem`,
  criadas automaticamente em bancos da 0.1.0 (`db.migrar()`).
- Dados de demonstração: 5 materiais (antes 2).

### Testes
- 53 testes automatizados (antes 29).

## [0.1.0] — outubro de 2026 (iteração 1, relatório parcial / CP3)
- MVP com login por perfil, check-in emocional, alertas, adaptação de materiais por regras
  para TDAH, TEA e dislexia, busca TF-IDF, indicadores do gestor e controles de LGPD.
- 29 testes automatizados.
