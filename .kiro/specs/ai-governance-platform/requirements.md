# Documento de Requisitos

## Introdução

O Nexus é uma plataforma de Governança de IA e Dados que centraliza a inteligência de projetos, avalia viabilidade técnica através de um Wizard com IA, e automatiza o caminho para a entrega de projetos. Este documento define os requisitos para uma prova de conceito (PoC) que demonstra as três fases do funil: Catálogo, Wizard e Entrega. A aplicação roda localmente com dados de amostra, utilizando Python/FastAPI no backend, HTML/JavaScript no frontend e SQLite como banco de dados.

## Glossário

- **Plataforma_Nexus**: A aplicação completa de governança de IA composta pelos módulos Catálogo, Wizard e Entrega.
- **Catálogo**: Módulo que agrega e exibe o registro unificado de projetos de IA e dados de múltiplas fontes, com objetivo descritivo e organizador.
- **Wizard**: Módulo de chat conversacional alimentado por LLM que descreve iniciativas do catalogo, analisa propostas, entende o problema e direciona usuários para soluções.
- **Entrega**: Módulo que fornece procedimentos operacionais e documentação para acessar as ferramentas recomendadas.
- **Projeto**: Um registro no catálogo representando uma iniciativa interna de IA ou dados.
- **Fonte**: A origem de um projeto (n8n, Lovable, TI, Deep, BI).
- **Ferramenta_Solução**: Uma das opções de ferramentas disponíveis: Copilot, Lovable, n8n, Alteryx, Equipe Deep (times internos de desenvolvimento de IA), Equipe BI, Squad de Desenvolvimento Interno, ou "Não temos solução hoje".
- **LLM_Local**: Modelo de linguagem executado localmente via Ollama ou llama-cpp-python.
- **Vector_Store**: Banco de dados vetorial ChromaDB usado para busca semântica no Catálogo.
- **Relatório_Executivo**: Resumo gerado a partir dos dados do Catálogo para stakeholders de nível C.
- **Procedimento_Acesso**: Instruções passo a passo para acessar uma ferramenta recomendada.

## Requisitos

### Requisito 1: Ingestão e Armazenamento de Dados do Catálogo

**User Story:** Como administrador da plataforma, eu quero importar dados de projetos a partir de arquivos locais (CSV, JSON), para que o Catálogo contenha informações unificadas de todas as fontes.

#### Critérios de Aceitação

1. QUANDO um arquivo CSV ou JSON é fornecido no diretório de dados, O Catálogo SHALL processar o arquivo e armazenar os registros de projetos no banco SQLite.
2. QUANDO um arquivo contém campos obrigatórios ausentes (nome, descrição, fonte), O Catálogo SHALL chamar LLM para sugerir preenchimento desses campos.
3. QUANDO projetos de múltiplas fontes são importados, O Catálogo SHALL unificar os registros em uma única tabela mantendo a rastreabilidade da fonte original.
4. QUANDO um projeto com o mesmo identificador já existe no banco, O Catálogo SHALL atualizar o registro existente em vez de criar duplicatas.

### Requisito 2: Visualização e Consulta do Catálogo

**User Story:** Como usuário da plataforma, eu quero visualizar e pesquisar projetos no Catálogo, para que eu possa encontrar informações sobre iniciativas existentes de IA e dados.

#### Critérios de Aceitação

1. QUANDO um usuário acessa a página do Catálogo, A Plataforma_Nexus SHALL exibir a lista de todos os projetos com nome, descrição, fonte e status.
2. QUANDO um usuário digita um termo de busca, O Catálogo SHALL filtrar os projetos cujo nome ou descrição contenham o termo pesquisado.
3. QUANDO um usuário seleciona um projeto da lista, O Catálogo SHALL exibir os detalhes completos do projeto incluindo descrição técnica, proprietário, fonte e status atual.
4. QUANDO um usuário aplica um filtro por fonte, O Catálogo SHALL exibir apenas os projetos originados da fonte selecionada.

### Requisito 3: Geração de Relatórios Executivos

**User Story:** Como stakeholder executivo, eu quero gerar relatórios resumidos do Catálogo, para que eu possa ter visibilidade sobre o portfólio de projetos de IA.

#### Critérios de Aceitação

1. QUANDO um usuário solicita um relatório executivo, A Plataforma_Nexus SHALL gerar um resumo contendo a contagem de projetos por fonte, por status e uma visão geral do portfólio.
2. QUANDO o relatório é gerado, A Plataforma_Nexus SHALL apresentar os dados em formato estruturado com tabelas e indicadores numéricos.

### Requisito 4: Chat Conversacional do Wizard

**User Story:** Como usuário da plataforma, eu quero interagir com um agente de chat inteligente, para que eu possa fazer perguntas sobre projetos de IA no catálogo ou submeter propostas de novos projetos.

#### Critérios de Aceitação

1. QUANDO um usuário envia uma mensagem no chat do Wizard, O Wizard SHALL processar a mensagem utilizando o LLM_Local e retornar uma resposta contextualizada.
2. QUANDO um usuário faz uma pergunta sobre projetos existentes, O Wizard SHALL consultar o Vector_Store para recuperar informações relevantes do Catálogo e incluí-las na resposta.
3. QUANDO o LLM_Local não está disponível ou retorna erro, O Wizard SHALL exibir uma mensagem de erro clara informando que o serviço de IA está indisponível.
4. QUANDO um usuário envia uma mensagem vazia ou composta apenas de espaços, O Wizard SHALL rejeitar a mensagem e manter o estado atual do chat.
5.QUANDO um usuário faz uma pergunta sobre projetos existentes e o Wizard não encontra informações, o Wizard SHALL responder "Não encontrei nenhum projeto similar, gostaria de propor um novo projeto?"

### Requisito 5: Análise de Viabilidade e Roteamento de Soluções

**User Story:** Como usuário da plataforma, eu quero que o Wizard analise minha proposta e me direcione para a ferramenta ou equipe mais adequada, para que eu saiba qual caminho seguir para executar meu projeto.

#### Critérios de Aceitação

1. QUANDO um usuário submete uma proposta de projeto, O Wizard SHALL analisar a proposta contra o Catálogo existente para identificar projetos similares ou redundantes.
2. QUANDO o Wizard identifica uma solução adequada, O Wizard SHALL recomendar uma Ferramenta_Solução específica dentre as opções disponíveis (Copilot, Lovable, n8n, Alteryx, Equipe Deep (times internos de desenvolvimento de IA), Equipe BI, Desenvolvimento Squad).
3. SE nenhuma solução existente atende à proposta, ENTÃO O Wizard SHALL responder explicitamente "Não temos uma solução disponível hoje" e sugerir o registro como nova demanda de inovação.
4. QUANDO o Wizard recomenda uma ferramenta, A resposta SHALL incluir uma justificativa clara do porquê aquela ferramenta foi selecionada.

### Requisito 6: Procedimentos de Entrega

**User Story:** Como usuário da plataforma, eu quero receber instruções claras sobre como acessar a ferramenta recomendada pelo Wizard, para que eu possa dar o próximo passo concreto no meu projeto.

#### Critérios de Aceitação

1. QUANDO o Wizard recomenda uma Ferramenta_Solução, A Plataforma_Nexus SHALL exibir o procedimento de acesso correspondente com instruções passo a passo.
2. QUANDO um procedimento de acesso possui documentação de apoio (PDF, template), A Entrega SHALL fornecer o link ou caminho para o arquivo de documentação.
3. QUANDO um usuário acessa o endpoint de entrega com um identificador de ferramenta, A Entrega SHALL retornar as instruções em formato estruturado (markdown ou JSON).
4. SE uma ferramenta não possui procedimento de acesso cadastrado, ENTÃO A Entrega SHALL informar que o procedimento está em elaboração e sugerir contato com a equipe responsável.

### Requisito 7: Interface Web Unificada

**User Story:** Como usuário da plataforma, eu quero acessar todas as funcionalidades através de uma interface web simples, para que eu possa navegar entre Catálogo, Wizard e Entrega de forma integrada.

#### Critérios de Aceitação

1. A Plataforma_Nexus SHALL fornecer uma interface web com navegação entre as três seções: Catálogo, Wizard e Entrega.
2. QUANDO um usuário navega entre seções, A Plataforma_Nexus SHALL manter o contexto da sessão sem perda de dados.
3. QUANDO a interface é carregada, A Plataforma_Nexus SHALL exibir o conteúdo de forma responsiva e acessível em navegadores modernos.

### Requisito 8: API Backend e Persistência

**User Story:** Como desenvolvedor, eu quero que a plataforma exponha endpoints REST bem definidos, para que o frontend possa consumir dados de forma estruturada.

#### Critérios de Aceitação

1. A Plataforma_Nexus SHALL expor endpoints REST para listar projetos, buscar projetos, gerar relatórios, enviar mensagens ao Wizard e consultar procedimentos de entrega.
2. QUANDO um endpoint recebe uma requisição com parâmetros inválidos, A Plataforma_Nexus SHALL retornar um código de erro HTTP apropriado com mensagem descritiva.
3. A Plataforma_Nexus SHALL validar todos os dados de entrada utilizando schemas Pydantic antes de processá-los.
4. A Plataforma_Nexus SHALL armazenar todos os dados persistentes no arquivo SQLite localizado em `./local_db/nexus.db`.

### Requisito 9: Dados de Amostra para Prova de Conceito

**User Story:** Como avaliador da PoC, eu quero que a plataforma venha com dados de amostra pré-carregados, para que eu possa testar todas as funcionalidades sem configuração adicional.

#### Critérios de Aceitação

1. A Plataforma_Nexus SHALL incluir arquivos de dados de amostra representando projetos de pelo menos 3 fontes diferentes (n8n, Deep, BI).
2. A Plataforma_Nexus SHALL incluir pelo menos 10 projetos de amostra com descrições técnicas realistas.
3. A Plataforma_Nexus SHALL incluir procedimentos de acesso de amostra para pelo menos 4 ferramentas diferentes.
4. QUANDO a aplicação é iniciada pela primeira vez, A Plataforma_Nexus SHALL carregar automaticamente os dados de amostra no banco SQLite e no Vector_Store.
