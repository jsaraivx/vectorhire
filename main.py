import os
import json
from src.extraction.pdf_extractor import PDFExtractor
from src.processing.text_chunker import chunk_text 
from src.vector_db.embedding_service import EmbeddingService
from src.vector_db.repository import VectorRepository

# Já vamos importar o serviço que você vai construir a seguir
from src.llm.matching_service import MatchingService

def run_ingestion(extract_pdfs: bool = False):
    """
    Fase 1 e 2: Extrai PDFs, fatia, gera vetores e salva no banco (Postgres).
    """
    print("=== INICIANDO PIPELINE DE INGESTÃO ===")
    
    if extract_pdfs:
        print("[1/4] Extraindo PDFs...")
        extractor = PDFExtractor()
        count = extractor.process_all()
        print(f"      Extraídos {count} PDF(s).")
    
    processed_folder = 'data/processed'
    processed_files = [f for f in os.listdir(processed_folder) if f.endswith('.txt')]
    
    if not processed_files:
        print(f"Nenhum arquivo processado encontrado em {processed_folder}")
        return
    
    refined_chunks = []
    
    print("[2/4] Fatiando os textos (Chunking)...")
    for file_name in processed_files:
        file_path = os.path.join(processed_folder, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                resume_text = f.read()
            chunks = chunk_text(resume_text, file_name)
            refined_chunks.extend(chunks)
        except Exception as e:
            print(f"      Erro ao processar {file_name}: {e}")
            
    print(f"      Total de chunks gerados: {len(refined_chunks)}")
    
    print("[3/4] Gerando Embeddings Locais (all-MiniLM-L6-v2)...")
    emb = EmbeddingService()
    payload_data = emb.generate_embeddings(refined_chunks)

    print("[4/4] Salvando no banco de dados vetorial (pgvector)...")
    repo = VectorRepository()
    repo.upsert_chunks(payload_data)
    
    print("=== INGESTÃO CONCLUÍDA COM SUCESSO ===\n")


def test_matching_engine():
    """
    Fase 3: Testa o motor de busca e o raciocínio do LLM.
    """
    print("=== INICIANDO MOTOR DE MATCHING (RAG) ===")
    
    # Uma descrição de vaga de teste focada em Engenharia de Dados
    vaga_teste = """
    Vaga: Engenheiro de Dados Pleno
    Requisitos Obrigatórios:
    - Sólida experiência com construção de pipelines ETL/ELT.
    - Domínio de Python e SQL.
    - Experiência prática com Google Cloud Platform (GCP), especificamente BigQuery e Pub Sub ou Kafka.
    - Conhecimento em orquestração de dados com Apache Airflow.
    - Desejável experiência com processamento em streaming (Kafka).
    """
    
    print(f"📋 Vaga alvo:\n{vaga_teste}")
    
    matcher = MatchingService()
    
    # IMPORTANTE: Garanta que o método no seu matching_service.py se chama avaliar_candidato_para_vaga (no plural)
    resultados = matcher.avaliar_candidato_para_vaga(vaga_teste)
    
    print("\nVereditos do Recrutador Virtual (LLM):\n")
    
    # Agora iteramos sobre o dicionário retornado { "nome_do_arquivo.txt": "string_json_do_llm" }
    for candidato, resultado_json in resultados.items():
        print(f"--- 👤 Candidato: {candidato} ---")
        try:
            # Transforma a string do LLM em um objeto Python e imprime formatado
            parsed_json = json.loads(resultado_json)
            print(json.dumps(parsed_json, indent=4, ensure_ascii=False))
        except json.JSONDecodeError:
            # Fallback caso a IA tenha falhado em retornar um JSON perfeito
            print(resultado_json)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    # COMENTE OU DESCOMENTE O QUE QUISER TESTAR
    
    # 1. Se precisar reprocessar os currículos, descomente a linha abaixo:
    run_ingestion(extract_pdfs=False) 
    
    # 2. Para testar a Missão 7 (O Cérebro RAG), deixe esta linha ativa:
    test_matching_engine()