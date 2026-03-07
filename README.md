# VectorHire (AI-Powered ATS Pipeline)

> **Status:** Em desenvolvimento ativo

Um sistema de *Applicant Tracking System* (ATS) focado na análise semântica de currículos. Este projeto utiliza técnicas avançadas de **Data Engineering** e **AI Engineering (RAG)** para extrair, vetorizar e cruzar perfis de candidatos com descrições de vagas, utilizando Modelos de Linguagem (LLMs) para gerar justificativas de match.

## Arquitetura e Tech Stack

O projeto é dividido em um pipeline de ingestão assíncrona e um motor de decisão baseado em LLM Agentic Workflow.

- **Linguagem Core:** Python 3.10+
- **Extração de Dados:** PyMuPDF (Processamento de layouts complexos de PDFs)
- **Validação e Parsing:** Pydantic (Structured Outputs)
- **Armazenamento Vetorial:** Pinecone (Vector Database para similaridade de cosseno)
- **Orquestração (Planejado):** Apache Airflow & Docker
- **Modelos de IA:**
  - *Embeddings:* Sentence Transformers (Local) / OpenAI API
  - *Raciocínio:* Modelos locais via Ollama / OpenAI GPT-4o-mini



## Roadmap do Projeto

### Fase 1: Fundação de Dados (Data Engineering)
- [x] Configuração do ambiente e estrutura de diretórios (`src/`, `data/`).
- [x] Motor de extração de texto bruto de PDFs de currículos (Camada Bronze).
- [x] Implementação de chunking de texto focado na semântica do currículo.
- [x] Validação de metadados usando `Pydantic` schemas.

### Fase 2: Banco Vetorial e Embeddings (AI Engineering)
- [ ] Geração de vetores matemáticos para cada chunk de texto.
- [ ] Configuração do Pinecone Index (Serverless).
- [ ] Rotina de `upsert` no Pinecone associando vetores aos metadados (Camada Silver).

### Fase 3: Motor de Matching (Retrieval & LLM)
- [ ] Vetorização dinâmica da descrição da vaga (Job Description).
- [ ] Busca de similaridade (Top K) no Pinecone.
- [ ] Agente LLM para cruzar requisitos obrigatórios vs. habilidades do candidato.
- [ ] Geração de saída estruturada (Aceito/Recusado + Justificativa detalhada).

### Fase 4: Orquestração e Escalabilidade
- [ ] Containerização da aplicação com Docker.
- [ ] Refatoração das rotinas de extração para rodar como DAGs no Apache Airflow.

## Como rodar localmente (Setup Inicial)

1. Clone este repositório.
2. Crie um ambiente virtual: `python -m venv venv`
3. Instale as dependências: `pip install -r requirements.txt`
4. Crie um arquivo `.env` na raiz do projeto (veja `.env.example`).