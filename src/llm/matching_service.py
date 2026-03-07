import os
import google.generativeai as genai
from pydantic import BaseModel, Field

from dotenv import load_dotenv
from src.vector_db.embedding_service import EmbeddingService
from src.vector_db.repository import VectorRepository

load_dotenv()

# 1. We define EXACTLY how we want the AI to respond
class CandidateEvaluation(BaseModel):
    score_fit: int = Field(description="Nota de 0 a 100 baseada no match entre currículo e vaga")
    decision: str = Field(description="DEVE SER EXATAMENTE: 'Aprovado para Entrevista' ou 'Reprovado'")
    technical_justification: str = Field(description="Explicação detalhada do porquê da nota, citando tecnologias do currículo.")


class MatchingService:
    def __init__(self):
        # Initialize connections
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")
            
        genai.configure(api_key=api_key)
        
        self.llm = genai.GenerativeModel('gemini-2.5-flash')
        
        self.embedding_service = EmbeddingService()
        self.db = VectorRepository()

    def evaluate_candidates_for_job(self, job_description: str) -> str:
        """
        Orchestrates RAG: Vectorizes job, searches database, and asks LLM to evaluate.
        """
        print("🤖 [1/4] Vectorizing Job Description...")

        jd_vector = []
        final_results = {}

        emb_jd = self.embedding_service.model.encode(job_description)

        jd_vector = emb_jd.tolist()

        print(job_description)

        print("🔍 [2/4] Searching for most relevant resume fragments in Postgres...")

        chunk_search = self.db.search_similar_chunks(jd_vector, 15)

        unique_candidates = set([c.file_name for c in chunk_search])
        print(f"🎯 Candidates found on radar: {unique_candidates}")

        # chunks_relevantes = self.db.search_similar_chunks(jd_vector, 5)

        for candidate in unique_candidates:
            print(f"Analyzing candidate {candidate}..")
            print("🧠 [3/4] Building context for LLM...")

            candidate_chunks = self.db.get_chunk_file_by_name(candidate)

            resume_context = f"\n\n".join(
                [c.text_content for c in candidate_chunks]
            )
            
            print("⚡ [4/4] Consulting Gemini 2.5 Flash...")
            
            # The System Prompt defines the rules of the game
            prompt = f"""
            Você é um Tech Recruiter Sênior super rigoroso.
            Sua missão é avaliar se o candidato atende aos requisitos da vaga abaixo, 
            baseando-se ÚNICA E EXCLUSIVAMENTE nos fragmentos de currículo fornecidos.
            
            DESCRIÇÃO DA VAGA (Requisitos):
            {job_description}
            
            FRAGMENTOS DO CURRÍCULO DO CANDIDATO:
            {resume_context}
            
            Siga estritamente o formato JSON solicitado, avaliando a aderência técnica.
            """

            # API call forcing structured output using Pydantic schema
            response = self.llm.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=CandidateEvaluation,
                    temperature=0.1 # Low temperature = less creativity, more analytical precision
                )
            )
            final_results[candidate] = response.text

        return final_results