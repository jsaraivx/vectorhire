import os
import json
from src.extraction.pdf_extractor import PDFExtractor
from src.processing.text_chunker import chunk_text 
from src.vector_db.embedding_service import EmbeddingService
from src.vector_db.repository import VectorRepository

from src.llm.matching_service import MatchingService

def run_ingestion(extract_pdfs: bool = False):
    """
    Phase 1 and 2: Extracts PDFs, chunks text, generates vectors and saves to database (Postgres).
    """
    print("=== STARTING INGESTION PIPELINE ===")
    
    if extract_pdfs:
        print("[1/4] Extracting PDFs...")
        extractor = PDFExtractor()
        count = extractor.process_all()
        print(f"      Extracted {count} PDF(s).")
    
    processed_folder = 'data/processed'
    processed_files = [f for f in os.listdir(processed_folder) if f.endswith('.txt')]
    
    if not processed_files:
        print(f"No processed files found in {processed_folder}")
        return
    
    refined_chunks = []
    
    print("[2/4] Chunking texts...")
    for file_name in processed_files:
        file_path = os.path.join(processed_folder, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                resume_text = f.read()
            chunks = chunk_text(resume_text, file_name)
            refined_chunks.extend(chunks)
        except Exception as e:
            print(f"      Error processing {file_name}: {e}")
            
    print(f"      Total chunks generated: {len(refined_chunks)}")
    
    print("[3/4] Generating Local Embeddings (all-MiniLM-L6-v2)...")
    emb = EmbeddingService()
    payload_data = emb.generate_embeddings(refined_chunks)

    print("[4/4] Saving to vector database (pgvector)...")
    repo = VectorRepository()
    repo.upsert_chunks(payload_data)
    
    print("=== INGESTION COMPLETED SUCCESSFULLY ===\n")


def test_matching_engine():
    """
    Phase 3: Tests the search engine and LLM reasoning.
    """
    print("=== STARTING MATCHING ENGINE (RAG) ===")
    
    # A test job description focused on Data Engineering
    test_job = """
    Vaga: Engenheiro de Dados Pleno
    Requisitos Obrigatórios:
    - Sólida experiência com construção de pipelines ETL/ELT.
    - Domínio de Python e SQL.
    - Experiência prática com Google Cloud Platform (GCP), especificamente BigQuery e Pub Sub ou Kafka.
    - Conhecimento em orquestração de dados com Apache Airflow.
    - Desejável experiência com processamento em streaming (Kafka).
    """
    
    print(f"📋 Target Position:\n{test_job}")
    
    matcher = MatchingService()
    
    # IMPORTANT: Make sure the method in your matching_service.py is called evaluate_candidates_for_job
    results = matcher.evaluate_candidates_for_job(test_job)
    
    print("\nVerdicts from Virtual Recruiter (LLM):\n")
    
    # Now we iterate over the returned dictionary { "filename.txt": "string_json_from_llm" }
    for candidate, result_json in results.items():
        print(f"--- 👤 Candidate: {candidate} ---")
        try:
            # Transform the LLM string into a Python object and print formatted
            parsed_json = json.loads(result_json)
            print(json.dumps(parsed_json, indent=4, ensure_ascii=False))
        except json.JSONDecodeError:
            # Fallback if the AI failed to return perfect JSON
            print(result_json)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    # COMMENT OR UNCOMMENT WHAT YOU WANT TO TEST
    
    # 1. If you need to reprocess resumes, uncomment the line below:
    run_ingestion(extract_pdfs=False) 
    
    # 2. To test Phase 3 (The RAG Brain), keep this line active:
    test_matching_engine()