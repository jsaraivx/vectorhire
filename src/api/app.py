import os
import json
import shutil
import asyncio
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.extraction.pdf_extractor import PDFExtractor
from src.processing.text_chunker import chunk_text 
from src.vector_db.embedding_service import EmbeddingService
from src.vector_db.repository import VectorRepository
from src.llm.matching_service import MatchingService

app = FastAPI(
    title="VectorHire ATS API",
    description="RAG Motor for semantic analysis of resumes.",
    version="1.0.0"
)

# Configuração de CORS (Permite que o Frontend HTML se comunique com esta API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, trocar '*' pela URL real do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "online", 
        "message": "Motor RAG respirando."
    }

@app.post("/api/v1/match")
async def match_candidates(
    job_description: str = Form(...), 
    files: list[UploadFile] = File(...)
):
    """
    Recebe a vaga via texto e uma lista de currículos em PDF.
    Salva os PDFs no disco e executa o pipeline de IA.
    """
    RAW_DIR = "data/raw"
    os.makedirs(RAW_DIR, exist_ok=True) 

    arquivos_salvos = []

    # persist on disk
    for file in files:
        caminho_completo = os.path.join(RAW_DIR, file.filename)

        with open(
            caminho_completo,
            "wb"
        ) as f:
            shutil.copyfileobj(file.file, f)
            
        arquivos_salvos.append(file.filename)

    try:
        print("\n[1/3] Iniciando Pipeline de Ingestão via API...")
        
        # 1. Extração (Lê de data/raw e joga para data/processed)
        extractor = PDFExtractor()
        extractor.process_all()
        
        # 2. Chunking (Fatiamento)
        processed_files = [f for f in os.listdir('data/processed') if f.endswith('.txt')]
        refined_chunks = []
        for file_name in processed_files:
            file_path = os.path.join('data/processed', file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                resume_text = f.read()
            refined_chunks.extend(chunk_text(resume_text, file_name))
                
        # 3. Embeddings e Banco Vetorial
        emb = EmbeddingService()
        payload_data = emb.generate_embeddings(refined_chunks)
        
        repo = VectorRepository()
        repo.upsert_chunks(payload_data)

        print("🧠 [2/3] Acionando o Motor RAG (Gemini)...")
        matcher = MatchingService()
        
        resultados_ia = matcher.evaluate_candidates_for_job(job_description) 

        # Converte as strings do Gemini em dicionários reais do Python
        resultados_limpos = {}
        for candidato, resposta_texto in resultados_ia.items():
            try:
                resultados_limpos[candidato] = json.loads(resposta_texto)
            except json.JSONDecodeError:
                resultados_limpos[candidato] = {"erro": "Falha ao ler o veredito da IA", "texto_bruto": resposta_texto}

        print("[3/3] Devolvendo resultados para o Frontend!")
        
        return {
            "status": "sucesso",
            "vaga_analisada": job_description,
            "resultados": resultados_limpos
        }
    
    except Exception as e:
        print(f"❌ Erro no pipeline: {str(e)}")
        return {"status": "erro", "detalhe": str(e)}