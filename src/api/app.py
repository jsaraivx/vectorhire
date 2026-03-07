from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
import os
import shutil


app = FastAPI(
    title="VectorHire ATS API",
    description="RAG Motor for semantic analysis of resumes.",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, trocar '*' pela URL real do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobRequest(BaseModel):
    job_description: str

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
    Salva os PDFs no disco e retorna sucesso.
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

    return {
        "mensagem": "Arquivos recebidos com sucesso",
        "vaga": job_description,
        "curriculos_salvos": arquivos_salvos
    }