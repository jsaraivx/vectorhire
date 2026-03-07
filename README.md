# VectorHire (AI-Powered ATS Pipeline)

> **Status:** Funcional (MVP Completo) - Fase 3 Finalizada

Um sistema de *Applicant Tracking System* (ATS) focado na análise semântica de currículos. Este projeto utiliza técnicas avançadas de **Data Engineering** e **AI Engineering (RAG)** para extrair, vetorizar e cruzar perfis de candidatos com descrições de vagas, utilizando Modelos de Linguagem (LLMs) para gerar justificativas de match.

## Arquitetura e Tech Stack

O projeto é dividido em um pipeline de ingestão assíncrona e um motor de decisão baseado em LLM Agentic Workflow.

- **Linguagem Core:** Python 3.10+
- **Extração de Dados:** PyMuPDF (Processamento de layouts complexos de PDFs)
- **Validação e Parsing:** Pydantic (Structured Outputs)
- **Armazenamento Vetorial:** PostgreSQL + pgvector (Vector Database para similaridade de cosseno)
- **ORM:** SQLAlchemy
- **Orquestração (Planejado):** Apache Airflow & Docker
- **Modelos de IA:**
  - *Embeddings:* Sentence Transformers (`all-MiniLM-L6-v2` Local)
  - *Raciocínio:* Google Gemini (2.5 Flash) via API



## Roadmap do Projeto

### Fase 1: Fundação de Dados (Data Engineering)
- [x] Configuração do ambiente e estrutura de diretórios (`src/`, `data/`).
- [x] Motor de extração de texto bruto de PDFs de currículos (Camada Bronze).
- [x] Implementação de chunking de texto focado na semântica do currículo.
- [x] Validação de metadados usando `Pydantic` schemas.

### Fase 2: Banco Vetorial e Embeddings (AI Engineering)
- [x] Geração de vetores matemáticos para cada chunk de texto.
- [x] Configuração do PostgreSQL com extensão pgvector.
- [x] Schemas SQLAlchemy para persistência de embeddings e metadados (Camada Silver).

### Fase 3: Motor de Matching (Retrieval & LLM)
- [x] Vetorização dinâmica da descrição da vaga (Job Description).
- [x] Busca de similaridade (Top K) no PostgreSQL com pgvector.
- [x] Agente LLM para cruzar requisitos obrigatórios vs. habilidades do candidato (Gemini 2.5 Flash).
- [x] Geração de saída estruturada (Aceito/Recusado + Justificativa detalhada com Pydantic).

### Fase 4: Orquestração e Escalabilidade
- [ ] Containerização da aplicação com Docker.
- [ ] Refatoração das rotinas de extração para rodar como DAGs no Apache Airflow.

## Como rodar localmente (Setup Inicial)

1. Clone este repositório.
2. Crie um ambiente virtual: `python -m venv venv`
3. Instale as dependências: `pip install -r requirements.txt`
4. Crie um arquivo `.env` na raiz do projeto configurando suas credenciais de banco e a `GEMINI_API_KEY` (veja `.env.example`).
5. Suba o banco de dados vetorial PostgreSQL com a extensão pgvector: `docker-compose up -d`
6. Edite o final do arquivo `main.py` para escolher qual parte testar e execute: `python main.py`
    - Você pode testar a ingestão dos PDFs ou testar diretamente o motor de RAG simulando as posições nas vagas alvo.