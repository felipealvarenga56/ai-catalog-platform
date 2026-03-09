# Aura Governance Platform

Aura é uma plataforma inteligente de Governança de IA & Dados que cataloga todas as iniciativas de IA da compania e conecta a estratégia corporativa à execução técnica. Ela centraliza a inteligência de projetos, avalia a viabilidade técnica de propostas de projetos por meio de um Wizard com IA e automatiza o caminho até a entrega dos projetos via orientações sobre qual caminho e quais ferramentas estão em compliance e licenciadas pela companhia.

Este repositório é uma prova de conceito experimental projetada para rodar inteiramente de forma local — sem dependências de nuvem, sem custos de API, sem infraestrutura complexa. Foi construído para que um Desenvolvedor Júnior consiga entender, depurar e estender.

## Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (HTML/JS)                │
│              Vanilla JS + Tailwind CDN              │
├─────────────────────────────────────────────────────┤
│                  FastAPI Backend                    │
│  /api/projects  /api/wizard  /api/delivery  /api/reports │
├──────────┬──────────┬───────────┬───────────────────┤
│  SQLite  │ ChromaDB │  Ollama   │  Arquivos Estáticos│
│(catálogo)│(vetores) │(LLM local)│ (PDFs/templates)  │
└──────────┴──────────┴───────────┴───────────────────┘
```

A plataforma segue uma arquitetura de funil em três fases:

1. **Catálogo** — Ingestão e unificação de dados de projetos de múltiplas fontes
2. **Wizard** — Análise e roteamento de propostas de projetos com IA
3. **Entrega** — Procedimentos operacionais para que os usuários comecem a usar as ferramentas recomendadas
4. **Relatório Executivo** - Visão executiva do estado atual do desenvolvimento de IA da companhia

## Stack Tecnológica

| Componente | Tecnologia | Por quê |
|---|---|---|
| Backend | Python 3.10+ / FastAPI | Leve, gera documentação Swagger automaticamente, fácil de depurar |
| Frontend | Vanilla HTML/JS + Tailwind CSS (CDN) | Zero etapa de build, sem overhead de framework |
| Banco de Dados | SQLite | Arquivo único, zero instalação, suporte nativo em Python |
| LLM | Ollama (local) | Privacidade de dados, zero custo de API, roda em hardware comum |
| Vector Store | ChromaDB | Busca vetorial persistente local para RAG |
| Validação de Dados | Pydantic | Schemas com tipagem segura, essencial para qualquer projeto de dados |

## Início Rápido

### Pré-requisitos

- Python 3.10+
- [Ollama](https://ollama.com/download) instalado e em execução

### Configuração

```bash
# Instalar dependências Python
pip install -r requirements.txt

# Baixar um modelo LLM (gemma3:4b recomendado para máquinas com 16GB de RAM)
ollama pull gemma3:4b

# Iniciar o Ollama (se ainda não estiver rodando)
ollama serve

# Iniciar a aplicação
uvicorn api.main:app --reload
```

Abra `http://localhost:8000` no seu navegador.

### Variáveis de Ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `LLM_BACKEND` | `ollama` | Backend do LLM: `ollama` ou `llama_cpp` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL do servidor Ollama |
| `OLLAMA_MODEL` | `gemma3:4b` | Modelo a ser usado para geração |
| `OLLAMA_TIMEOUT` | `120` | Timeout de requisição em segundos |
| `LLAMA_MODEL_PATH` | — | Caminho para o arquivo GGUF (apenas para backend `llama_cpp`) |


## Abas da Plataforma

### Catálogo

O Catálogo é a fonte universal de verdade para todas as iniciativas de IA e dados da organização. Ele agrega informações de projetos de equipes distintas — Data Science (Deep), Business Intelligence (BI), TI (TI), automação (n8n), apps low-code (Lovable, Superblocks) e ferramentas de produtividade (Alteryx, Copilot) — em um único registro pesquisável.

**Por que existe:** Em grandes organizações, equipes frequentemente constroem soluções redundantes porque não sabem o que já existe. O Catálogo resolve isso tornando cada iniciativa visível e pesquisável. Antes de iniciar um novo projeto, é possível verificar se algo similar já existe, quem é o responsável e qual o status atual.

**O que exibe:**
- Lista unificada de todos os contratos de dados registrados (projetos/iniciativas)
- Busca por nome ou descrição com filtragem full-text
- Filtro por tipo de iniciativa (BI, Deep, n8n, Lovable, etc.)
- Visualização detalhada de cada contrato incluindo responsável, status, área, custo e retorno projetado
- Geração de relatório executivo com um clique

**API:** `GET /api/projects` com parâmetros opcionais `search`, `source`, `status`.

### Wizard (Assistente IA)

O Wizard é uma interface conversacional alimentada por LLM que atua como um consultor agêntico. Quando um usuário descreve uma necessidade ou proposta de projeto, o Wizard pesquisa o Catálogo via busca semântica (RAG), analisa a solicitação contra iniciativas existentes e recomenda o caminho de desenvolvimento mais eficiente.

**Por que existe:** Nem todos na organização sabem qual equipe ou ferramenta é mais adequada para seu problema. O Wizard preenche essa lacuna de conhecimento atuando como um concierge — ele entende a solicitação, verifica soluções existentes e direciona o usuário ao recurso correto. Também previne construções redundantes ao sinalizar quando um projeto similar já existe.

**Como funciona:**
1. O usuário descreve sua necessidade em linguagem natural (português suportado)
2. O ChromaDB realiza busca semântica no Catálogo para encontrar projetos similares
3. O pipeline RAG enriquece o prompt com contexto relevante do catálogo
4. O LLM local (Ollama) gera uma resposta estruturada com recomendação de ferramenta/equipe
5. O motor de roteamento extrai a recomendação e mapeia para uma `ToolSolution`

**Destinos de roteamento disponíveis:**
- **Self-Service:** Copilot, Lovable, n8n, Alteryx
- **Equipes Especializadas:** Deep (IA/Data Science), Equipe de BI
- **Build Estratégico:** Desenvolvimento com Squad Completo
- **Detecção de Lacuna:** "Não temos uma solução disponível hoje" — dispara solicitação de inovação

**API:** `POST /api/wizard/chat` com body `{ "message": "..." }`.

### Entrega

A Entrega é o habilitador de última milha. Após o Wizard recomendar uma ferramenta ou equipe, o usuário precisa saber *como* obter acesso e começar a trabalhar. A Entrega fornece procedimentos operacionais passo a passo para cada ferramenta — quem contatar, quais formulários preencher, quais aprovações são necessárias e onde encontrar documentação.

**Por que existe:** Uma recomendação é inútil se o usuário não sabe como agir. Em ambientes corporativos, obter acesso a uma ferramenta frequentemente envolve tickets de service desk, aprovações de gestores e revisões de segurança. A Entrega elimina a incerteza fornecendo instruções claras e acionáveis para cada caminho recomendado.

**O que exibe:**
- Grid de cards com todas as ferramentas e equipes disponíveis
- Procedimentos de acesso passo a passo para cada ferramenta
- Informações de contato da equipe responsável
- Links para documentação e templates

**API:** `GET /api/delivery/tools` e `GET /api/delivery/instructions/{tool_id}`.

### Relatório Executivo

O Relatório Executivo é um dashboard de governança projetado para stakeholders C-level e diretores. Ele fornece uma visão panorâmica de todas as iniciativas de IA e dados com KPIs, gráficos, tabulações cruzadas e métricas financeiras.

**Por que existe:** A liderança precisa entender o portfólio de iniciativas de IA/dados sem mergulhar em detalhes técnicos. Este dashboard responde perguntas como: Quantos projetos estão ativos? Quais áreas têm mais iniciativas? Qual o investimento total? Os projetos estão devidamente documentados e aprovados pela segurança? Ele possibilita decisões de alocação de recursos baseadas em dados.

**O que exibe:**
- Cards de KPI: total de contratos, quantidade ativos, em desenvolvimento, % conformidade de segurança, % conformidade de documentação, % cobertura de custo, % cobertura de retorno
- Gráficos: contratos por iniciativa, por status, por área, por responsável
- Tabulações cruzadas: área × iniciativa, área × status
- Resumo financeiro: custo e retorno projetado por iniciativa
- Filtros: área, iniciativa, status, responsável — todos combináveis

**API:** `GET /api/reports/executive-dashboard` com parâmetros de filtro opcionais.


## Contrato de Dados

O Contrato de Dados é o modelo de dados central da plataforma Aura. Toda iniciativa de IA ou dados registrada no Catálogo é representada como um contrato — um documento estruturado que captura os metadados técnicos, operacionais e de governança de um projeto.

### Por que Contratos de Dados?

Em organizações com dezenas de iniciativas de dados e IA espalhadas por múltiplas equipes, não existe uma forma padrão de descrever o que um projeto faz, quem é o responsável, quanto custa ou se foi aprovado pela segurança. Os contratos de dados resolvem isso impondo um schema consistente em todas as iniciativas, independente da equipe ou tecnologia por trás delas.

Isso possibilita:
- **Descoberta** — qualquer pessoa pode buscar e encontrar iniciativas existentes
- **Governança** — a liderança pode auditar conformidade (aprovações de segurança, documentação)
- **Visibilidade financeira** — custo e retorno projetado são rastreados por iniciativa
- **Prevenção de redundância** — o Wizard pode comparar novas propostas contra contratos existentes

### Schema do Contrato

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `business_map_id` | string | Sim | Identificador único do mapa de negócios (ex: `BM-001`) |
| `title` | string | Sim | Nome legível do projeto |
| `area` | string | Sim | Área de negócio / diretoria stakeholder |
| `contact_name` | string | Não | Nome da pessoa de contato principal |
| `contact_email` | string | Não | Email do contato principal |
| `sec_approval` | string | Não | Link para documento de aprovação de segurança |
| `docs_link` | string | Não | Link para documentação técnica |
| `cost` | string | Não | Custo mensal de cloud/infraestrutura (ex: "R$18.000,00/mês") |
| `projected_return` | string | Não | Retorno financeiro esperado ou impacto no negócio |
| `usage` | string | Não | Descrição operacional de como o projeto é usado em produção |
| `limitations` | string | Não | Limitações ou restrições conhecidas |

### Formato Texto do Contrato

Contratos também podem ser ingeridos a partir de um formato de texto estruturado (arquivos `.txt`). O parser (`api/contract_parser.py`) lê arquivos seguindo este template:

```
dataAI_Contract
id: 556706 (businessMap)
info:
  title: Recusa de oferta de vacina
  area: Operações de Farmácia
  initiative: Deep
  version: 1.0.0
  description:
    Descrição detalhada em múltiplas linhas da iniciativa...
```

**Dados de exemplo incluídos:**
1. **`data/samples/contracts_catalog.json`** — Catálogo em massa no formato JSON array (70 contratos)
2. **`data/samples/dataAI_Contract_ex1.txt`** — Contrato individual em formato texto (1 contrato)

Todos os contratos são armazenados no SQLite e indexados no ChromaDB para busca semântica.

## Estrutura do Projeto

```
├── api/                    # Backend FastAPI
│   ├── main.py             # Ponto de entrada da aplicação e lifespan
│   ├── models.py           # Schemas Pydantic e enums
│   ├── database.py         # Conexão SQLite e criação de tabelas
│   ├── ingestion.py        # Seed de dados a partir de arquivos de exemplo
│   ├── contract_parser.py  # Parser de contratos em formato texto
│   ├── llm_client.py       # Abstração do LLM local (Ollama / llama-cpp)
│   ├── rag.py              # Pipeline RAG: ChromaDB + LLM
│   ├── routing.py          # Mapeamento resposta LLM → ToolSolution
│   └── routes/             # Handlers de rotas da API
│       ├── projects.py     # Endpoints /api/projects
│       ├── wizard.py       # Endpoint /api/wizard/chat
│       ├── delivery.py     # Endpoints /api/delivery
│       └── reports.py      # Endpoints /api/reports
├── frontend/               # Frontend estático HTML/JS
│   ├── index.html          # Aplicação single-page
│   └── app.js              # Lógica do frontend
├── data/
│   ├── samples/            # Dados de exemplo para seed
│   └── delivery/           # Templates e guias em PDF
├── local_db/               # Armazenamento SQLite + ChromaDB (gitignored)
├── tests/                  # Suite de testes Pytest + Hypothesis
└── requirements.txt        # Dependências Python
```

## Executando os Testes

```bash
pytest tests/ -v
```

Testes baseados em propriedades usam [Hypothesis](https://hypothesis.readthedocs.io/) para geração automatizada de inputs.

## Licença

Prova de conceito interna — não destinada à distribuição pública.
