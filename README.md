# VectorHire (AI-Powered ATS Pipeline)

> **Status:** Funcional (Produto B2B Completo) - Processamento End-to-End validado.

## Screenshots

### UI - Dashboard Principal
![Dashboard Principal](assets/vector_hire_first_page.jpg)

### UI - Análise Técnica do Candidato
![Análise do Candidato](assets/vectorhire_candidate_analysis.jpg)

### Backend - Pipeline RAG (FastAPI + Gemini)
![Pipeline Backend](assets/vectorhire_api.jpg)


Um sistema de *Applicant Tracking System* (ATS) inteligente focado na análise semântica de currículos. Construído com técnicas avançadas de **Data Engineering** e **AI Engineering (RAG)**, o VectorHire extrai o texto de PDFs, vetoriza os dados, busca similaridade contra os requisitos de uma vaga e utiliza Modelos de Linguagem (LLMs) para decidir aprovação/reprovação de candidatos, além de extrair contatos úteis (GitHub, LinkedIn).

## Arquitetura e Tech Stack

O projeto opera em um modelo Client-Server com um pipeline de ingestão Two-Step RAG (Retrieval-Augmented Generation):

- **Backend / API:** FastAPI (Async API, lidando nativamente com `multipart/form-data`)
- **Extração de Dados:** PyMuPDF (`fitz`) para OCR interno de PDFs.
- **Processamento:** Semantic Chunking para fatiar o currículo sem perder contexto de ferramentas.
- **Banco Vetorial:** PostgreSQL + extensão `pgvector`.
- **ORM & Pattern:** SQLAlchemy implementando Repository Pattern.
- **Modelos de IA:**
  - *Embeddings Locais:* `sentence-transformers/all-MiniLM-L6-v2`
  - *LLM / Raciocínio:* Google Gemini 2.5 Flash via `google-generativeai`
- **Output Estruturado:** Pydantic (Garantindo que a IA retorne um JSON exato)
- **Frontend UI:** HTML5/CSS Vanilla com design SaaS Premium (Glassmorphism + Dark Mode), consumindo via Fetch API.

---

## Guia de Uso: Como rodar o projeto localmente

Siga o passo a passo abaixo para subir a aplicação por completo.

### 1. Requisitos do Sistema
- Python 3.10 ou superior (Recomendo a versão 3.11)
- Docker e Docker Compose (para subir o banco de dados)
- Uma chave de API válida do [Google AI Studio (Gemini)](https://aistudio.google.com/)

### 2. Configuração do Ambiente e Dependências

Clone este repositório e crie um ambiente virtual:

```bash
# Clone o repositório e entre na pasta
git clone <URL_DO_REPO>
cd vectorhire

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # No macOS/Linux
# venv\Scripts\activate   # No Windows

# Instale os pacotes (inclui FastAPI, SQLAlchemy, transformers, google-generativeai, etc.)
pip install -r requirements.txt
```

### 3. Configuração de Credenciais (`.env`)

Crie um arquivo `.env` na raiz do projeto com base nas chaves usadas no código. O arquivo precisa conter:

```env
# Conexão com o Banco de Dados Local (Postgres + pgvector via Docker)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/vectorhire

# Chave de API do Google Gemini
GEMINI_API_KEY=sua_chave_aqui
```

### 4. Executando o Projeto de Forma Automática (Recomendado)

Na raiz do projeto existem scripts prontos para subir tanto o banco local quanto a inteligência do Backend em apenas 1 clique:

**Para Mac e Linux:**
```bash
# Na primeira vez, dê permissão de execução:
chmod +x start.sh

# Para rodar (Sobe o Docker e a API):
./start.sh
```

**Para Windows:**
Basta dar um duplo clique (ou rodar no CMD) o arquivo:
```cmd
start.bat
```

**Para Desligar e Limpar o Ambiente:**
Se quiser derrubar o banco de dados (Docker) e limpar a memória física do seu HD gerada pelos PDFs (`data/raw`), rodar o script de destruição:
- Mac/Linux: `./destroy.sh`
- Windows: `destroy.bat`

> *Se você preferir rodar manualmente:*
> `docker-compose up -d` e depois `uvicorn src.api.app:app --reload --port 8000`

### 5. Acessando a Interface Frontend (ATS UI)

Diferente de sistemas complexos de build, o Frontend foi construído de forma completamente desacoplada e limpa usando HTML, CSS e JS puros. O Backend já está exposto com `CORSMiddleware` liberado.

**Para interagir com o VectorHire:**
1. Abra seu navegador (Chrome, Edge, Safari).
2. Vá até a pasta `frontend/` deste projeto.
3. Arraste ou dê duplo clique no arquivo `index.html`. Ele abrirá no navegador de imediato com a barra de endereço indicando `file:///.../frontend/index.html`.

**Fluxo de Teste:**
- No painel aberto, descreva uma vaga focada em "Engenharia de Dados GCP e Python" na caixa de texto.
- Faça o drag & drop (ou clique para anexar) alguns currículos reais em PDF.
- Clique em **"Analisar Candidatos"**.
- Acompanhe no terminal a evolução do **Pipeline RAG** (Extração -> Chunking -> Embeddings -> Busca de Similaridade -> Parecer do Gemini).
- Os cards renderização em segundos na UI com o Veredito da IA e os ícones de contato extraídos (GitHub, LinkedIn, Email).

---

## Cost Analysis: Previsão de Consumo da LLM (Gemini)

Para cada **currículo selecionado** para análise (ou seja, os currículos que passaram no filtro matemático inicial do Postgres/pgvector), o VectorHire faz **uma requisição (1 request)** para a API do Google Gemini.

### Estimativa para 1 Currículo Avaliado:
- **Input (Prompt + Vaga + Currículo Completo):** ~1.000 a 1.500 tokens. (Depende do tamanho em páginas de um PDF comum).
- **Output (Resposta Pydantic JSON):** ~150 a 250 tokens (Varia pelo tamanho da "Justificativa Técnica" gerada).
- **Total de Tokens por Currículo:** **~1.300 a 1.750 tokens**.

### Custos na Vida Real (Com o *Gemini 2.5 Flash*):
Atualmente, a API do Gemini 2.5 Flash é **gratuita sob o Free Tier** (até 15 requisições por minuto e 1 milhão de tokens por minuto). Logo, para uso pessoal/portfólio, **o custo será $0.00**.

> **Nota Econômica:** O RAG implementado no VectorHire economiza drasticamente o uso da API ao rodar a vetorização (`embeddings`) **localmente na sua máquina** pela biblioteca `sentence-transformers`. Só enviamos texto para a API rodar a inferência inteligente final nos candidatos que **já fizeram sentido** estatisticamente.

---

## Features Implementadas

- [x] Ingestão baseada em upload de arquivos físicos via rota `/api/v1/match`.
- [x] Limpeza e persistência dos binários em `data/raw`.
- [x] Embeddings gerados de forma local (economia absurda de API LLM).
- [x] Busca matemática de metadados (`LIMIT 15` fragmentos mais relevantes do Banco PgVector).
- [x] Uso de *Pydantic Strict Schema* para o Agente Gemini nunca falhar no contrato JSON com o Frontend.
- [x] UI Premium B2B responsiva p/ Desktop ou Mobile.