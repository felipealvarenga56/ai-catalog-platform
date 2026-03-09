# Plano de Implementação: Nexus Governance Platform

## Visão Geral

Implementação incremental da PoC Nexus em Python/FastAPI, começando pela camada de dados e modelos, seguindo pelos três módulos (Catálogo, Wizard, Entrega), frontend e dados de amostra. Cada etapa constrói sobre a anterior e inclui testes para validação contínua.

## Tarefas

- [x] 1. Estrutura do projeto e camada de dados
  - [x] 1.1 Criar estrutura de diretórios e arquivos iniciais
    - Criar `api/__init__.py`, `api/main.py`, `api/database.py`, `api/models.py`
    - Criar `api/routes/__init__.py`
    - Criar `requirements.txt` com dependências (fastapi, uvicorn, pydantic, sqlalchemy, chromadb, httpx, hypothesis, pytest)
    - Criar diretórios `data/samples/`, `data/delivery/`, `local_db/`, `frontend/`
    - _Requisitos: 8.4_

  - [x] 1.2 Implementar modelos Pydantic e schemas
    - Criar todos os schemas em `api/models.py`: `ProjectSource`, `ProjectStatus`, `ProjectCreate`, `Project`, `ChatMessage`, `ToolSolution`, `WizardResponse`, `DeliveryProcedure`, `ExecutiveReport`, `IngestResult`
    - _Requisitos: 8.3_

  - [x] 1.3 Implementar conexão SQLite e criação de tabelas
    - Criar `api/database.py` com funções de conexão, criação de tabelas `projects` e `delivery_procedures`
    - Banco em `./local_db/nexus.db`
    - _Requisitos: 8.4_

- [-] 2. Módulo Catálogo - Ingestão e API
  - [x] 2.1 Implementar serviço de ingestão
    - Criar `api/ingestion.py` com `ingest_file()` que lê CSV/JSON, valida campos obrigatórios, faz upsert no SQLite
    - Implementar lógica de rejeição para registros com campos ausentes
    - Implementar upsert por (nome + fonte) para evitar duplicatas
    - _Requisitos: 1.1, 1.2, 1.3, 1.4_

  - [ ]* 2.2 Escrever teste de propriedade para round-trip de ingestão
    - **Propriedade 1: Round-trip de ingestão com preservação de fonte**
    - **Valida: Requisitos 1.1, 1.3**

  - [ ]* 2.3 Escrever teste de propriedade para rejeição de registros inválidos
    - **Propriedade 2: Rejeição de registros inválidos na ingestão**
    - **Valida: Requisito 1.2**

  - [ ]* 2.4 Escrever teste de propriedade para idempotência de upsert
    - **Propriedade 3: Idempotência de upsert**
    - **Valida: Requisito 1.4**

  - [x] 2.5 Implementar endpoints do Catálogo
    - Criar `api/routes/projects.py` com `GET /api/projects` (listagem, busca por termo, filtro por fonte), `GET /api/projects/{project_id}` (detalhes)
    - _Requisitos: 2.1, 2.2, 2.3, 2.4_

  - [ ]* 2.6 Escrever teste de propriedade para corretude de filtros
    - **Propriedade 4: Corretude de filtros de busca e fonte**
    - **Valida: Requisitos 2.2, 2.4**

  - [ ]* 2.7 Escrever teste de propriedade para round-trip de detalhes
    - **Propriedade 5: Round-trip de detalhes do projeto**
    - **Valida: Requisito 2.3**

  - [x] 2.8 Implementar endpoint de relatório executivo
    - Criar `api/routes/reports.py` com `GET /api/reports/executive`
    - Retornar contagem por fonte, por status e total
    - _Requisitos: 3.1, 3.2_

  - [ ]* 2.9 Escrever teste de propriedade para consistência do relatório
    - **Propriedade 6: Consistência de contagens no relatório executivo**
    - **Valida: Requisito 3.1**

- [x] 3. Checkpoint - Verificar módulo Catálogo
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

- [x] 4. Módulo Wizard - RAG e Roteamento
  - [x] 4.1 Implementar integração com ChromaDB
    - Criar funções em `api/rag.py` para indexar projetos no ChromaDB e fazer busca semântica (`query_catalog`)
    - _Requisitos: 4.2_

  - [x] 4.2 Implementar pipeline RAG e integração com Ollama
    - Criar `build_prompt()` e `get_llm_response()` em `api/rag.py`
    - Implementar chamada HTTP ao Ollama local com tratamento de erros (indisponível, timeout)
    - _Requisitos: 4.1, 4.3_

  - [x] 4.3 Implementar lógica de roteamento de ferramentas
    - Criar `api/routing.py` com `extract_recommendation()` que mapeia a resposta do LLM para um `ToolSolution`
    - Incluir lógica para "Não temos solução hoje" quando nenhuma ferramenta se aplica
    - _Requisitos: 5.1, 5.2, 5.3, 5.4_

  - [x] 4.4 Implementar endpoint do Wizard
    - Criar `api/routes/wizard.py` com `POST /api/wizard/chat`
    - Validar mensagem não vazia, executar pipeline RAG, retornar `WizardResponse`
    - _Requisitos: 4.1, 4.4, 5.2_

  - [ ]* 4.5 Escrever teste de propriedade para rejeição de whitespace
    - **Propriedade 7: Rejeição de mensagens em branco no Wizard**
    - **Valida: Requisito 4.4**

  - [ ]* 4.6 Escrever teste de propriedade para validade da recomendação
    - **Propriedade 8: Validade da recomendação do Wizard**
    - **Valida: Requisitos 5.2, 5.4**

  - [ ]* 4.7 Escrever testes unitários para erros do Wizard
    - Testar LLM indisponível retorna HTTP 503 (Requisito 4.3)
    - Testar resposta "Não temos solução" quando tool é NO_SOLUTION (Requisito 5.3)
    - _Requisitos: 4.3, 5.3_

- [x] 5. Módulo Entrega - Procedimentos
  - [x] 5.1 Implementar endpoints de Entrega
    - Criar `api/routes/delivery.py` com `GET /api/delivery/instructions/{tool_id}` e `GET /api/delivery/tools`
    - Implementar fallback para tool_id sem procedimento cadastrado
    - _Requisitos: 6.1, 6.2, 6.3, 6.4_

  - [ ]* 5.2 Escrever teste de propriedade para completude da entrega
    - **Propriedade 9: Completude do procedimento de entrega**
    - **Valida: Requisitos 6.1, 6.2, 6.3**

  - [ ]* 5.3 Escrever testes unitários para erros de Entrega
    - Testar tool_id inexistente retorna fallback (Requisito 6.4)
    - _Requisitos: 6.4_

- [x] 6. Checkpoint - Verificar módulos Wizard e Entrega
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

- [x] 7. Dados de amostra e inicialização
  - [x] 7.1 Criar arquivos de dados de amostra
    - Criar CSVs/JSONs em `data/samples/` com pelo menos 10 projetos de 3+ fontes (n8n, Deep, BI)
      - n8n: gerar exemplos de projetos simples e factíveis de serem desenvolvidos na ferramenta n8n por parte de uma empresa de varejo farmaceutico (raia Drogasil)
      - deep: gerar exemplos de projetos de AI e ML desenvolvidos por especialistas em AI e ML, cientistas de dados do time de experts da raia drogasil
      -BI projetos gerados pelo time de analistas de BI da raia drogasil
    - Criar procedimentos de acesso de amostra para pelo menos 4 ferramentas
    - _Requisitos: 9.1, 9.2, 9.3_

  - [x] 7.2 Implementar seed automático na inicialização
    - Criar `seed_sample_data()` em `api/ingestion.py`
    - Chamar no startup do FastAPI para carregar dados no SQLite e ChromaDB
    - _Requisitos: 9.4_

  - [ ]* 7.3 Escrever testes unitários para dados de amostra
    - Verificar >= 3 fontes, >= 10 projetos, >= 4 procedimentos após seed
    - _Requisitos: 9.1, 9.2, 9.3, 9.4_

- [x] 8. API principal e validação
  - [x] 8.1 Montar aplicação FastAPI e registrar rotas
    - Criar `api/main.py` com app FastAPI, registrar todos os routers, configurar CORS, servir arquivos estáticos do frontend
    - Configurar startup event para seed de dados
    - _Requisitos: 8.1, 8.2_

  - [ ]* 8.2 Escrever teste de propriedade para tratamento de erros
    - **Propriedade 10: Tratamento de erros para entrada inválida**
    - **Valida: Requisito 8.2**

  - [ ]* 8.3 Escrever testes unitários para endpoints REST
    - Verificar que todos os endpoints existem e respondem
    - Verificar que banco é criado em ./local_db/nexus.db
    - _Requisitos: 8.1, 8.4_

- [x] 9. Frontend
  - [x] 9.1 Criar página principal com navegação
    - Criar `frontend/index.html` com layout Tailwind CSS e navegação entre Catálogo, Wizard e Entrega
    - _Requisitos: 7.1, 7.3_

  - [x] 9.2 Criar página do Catálogo
    - Criar `frontend/catalogo.html` com lista de projetos, busca, filtro por fonte e botão de relatório executivo
    - _Requisitos: 2.1, 2.2, 2.4, 3.1_

  - [x] 9.3 Criar página do Wizard
    - Criar `frontend/wizard.html` com interface de chat para interação com o Wizard
    - _Requisitos: 4.1, 5.2_

  - [x] 9.4 Criar página de Entrega
    - Criar `frontend/entrega.html` com exibição de procedimentos de acesso
    - _Requisitos: 6.1, 6.2_

  - [x] 9.5 Implementar lógica JavaScript
    - Criar `frontend/app.js` com chamadas à API, renderização de dados e gerenciamento de navegação
    - _Requisitos: 7.1, 7.2_

- [x] 10. Checkpoint final
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

## Notas

- Tarefas marcadas com `*` são opcionais e podem ser puladas para um MVP mais rápido
- Cada tarefa referencia requisitos específicos para rastreabilidade
- Checkpoints garantem validação incremental
- Testes de propriedade validam propriedades universais de corretude
- Testes unitários validam exemplos específicos e casos de borda
