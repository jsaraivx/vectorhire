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

from fastapi.responses import StreamingResponse

@app.post("/api/v1/match")
async def match_candidates(
    job_description: str = Form(...), 
    files: list[UploadFile] = File(...)
):
    """
    Recebe a vaga via texto e uma lista de currículos em PDF.
    Salva os PDFs no disco e executa o pipeline de IA emitindo stream SSE.
    """
    RAW_DIR = "data/raw"
    os.makedirs(RAW_DIR, exist_ok=True) 

    # persist on disk immediately
    for file in files:
        caminho_completo = os.path.join(RAW_DIR, file.filename)
        with open(caminho_completo, "wb") as f:
            shutil.copyfileobj(file.file, f)

    async def event_generator():
        try:
            print("\n[1/3] Iniciando Pipeline de Ingestão via API Streaming...")
            yield f"data: {json.dumps({'status': 'info', 'message': 'Extraindo texto bruto dos PDFs com OCR...'})}\n\n"
            
            # 1. Extração (Lê de data/raw e joga para data/processed)
            extractor = PDFExtractor()
            extractor.process_all()
            
            yield f"data: {json.dumps({'status': 'info', 'message': 'Quebrando currículos em fragmentos sintáticos...'})}\n\n"
            
            # 2. Chunking (Fatiamento)
            processed_files = [f for f in os.listdir('data/processed') if f.endswith('.txt')]
            refined_chunks = []
            for file_name in processed_files:
                file_path = os.path.join('data/processed', file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    resume_text = f.read()
                refined_chunks.extend(chunk_text(resume_text, file_name))
                    
            yield f"data: {json.dumps({'status': 'info', 'message': 'Gerando Embeddings Vetoriais locais...'})}\n\n"
            
            # 3. Embeddings e Banco Vetorial
            emb = EmbeddingService()
            payload_data = emb.generate_embeddings(refined_chunks)
            
            yield f"data: {json.dumps({'status': 'info', 'message': 'Sincronizando fragmentos no PostgreSQL + pgvector...'})}\n\n"
            
            repo = VectorRepository()
            repo.upsert_chunks(payload_data)

            print("🧠 [2/3] Acionando o Motor RAG (Gemini) em Streaming...")
            matcher = MatchingService()
            
            for update in matcher.evaluate_candidates_for_job_stream(job_description):
                yield f"data: {json.dumps(update)}\n\n"
                
        except Exception as e:
            print(f"❌ Erro no pipeline: {str(e)}")
            error_msg = str(e)
            is_quota = "429" in error_msg or "quota" in error_msg.lower() or "exhausted" in error_msg.lower()
            yield f"data: {json.dumps({'status': 'erro', 'message': error_msg, 'is_quota': is_quota})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")