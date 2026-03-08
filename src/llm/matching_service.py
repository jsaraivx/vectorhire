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
    github_url: str = Field(description="URL do perfil GitHub do candidato. Retorne string vazia '' se não encontrada.")
    linkedin_url: str = Field(description="URL do perfil LinkedIn do candidato. Retorne string vazia '' se não encontrada.")
    email: str = Field(description="E-mail de contato do candidato. Retorne string vazia '' se não encontrado.")
    phone: str = Field(description="Telefone de contato do candidato. Retorne string vazia '' se não encontrado.")


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

    def evaluate_candidates_for_job_stream(self, job_description: str):
        """
        Orchestrates RAG: Vectorizes job, searches database, and asks LLM to evaluate.
        Yields progress updates for SSE streaming.
        """
        yield {"status": "info", "message": "Vetorizando a vaga (Job Description)..."}

        jd_vector = []
        final_results = {}

        emb_jd = self.embedding_service.model.encode(job_description)
        jd_vector = emb_jd.tolist()

        yield {"status": "info", "message": "Buscando fragmentos mais relevantes no banco de dados vetorial..."}

        chunk_search = self.db.search_similar_chunks(jd_vector, 15)
        unique_candidates = set([c.file_name for c in chunk_search])
        
        total_candidates = len(unique_candidates)
        yield {"status": "info", "message": f"{total_candidates} currículos aderentes encontrados. Iniciando inferência profunda..."}

        for i, candidate in enumerate(unique_candidates):
            
            nome_display = candidate.replace(".pdf", "").replace(".txt", "")
            if len(nome_display) > 25:
                nome_display = nome_display[:22] + "..."
                
            yield {"status": "progress", "message": f"🤖 Analisando candidato {i+1} de {total_candidates}: {nome_display}"}

            candidate_chunks = self.db.get_chunk_file_by_name(candidate)

            resume_context = f"\n\n".join(
                [c.text_content for c in candidate_chunks]
            )
            
            # The System Prompt defines the rules of the game
            prompt = f"""
            Você é um Tech Recruiter Sênior super rigoroso.
            Sua missão é avaliar se o candidato atende aos requisitos da vaga abaixo, 
            baseando-se ÚNICA E EXCLUSIVAMENTE nos fragmentos de currículo fornecidos.
            
            Além da avaliação técnica, EXTRAIA as seguintes informações de contato do candidato
            se estiverem presentes nos fragmentos:
            - URL do GitHub (ex: github.com/usuario)
            - URL do LinkedIn (ex: linkedin.com/in/usuario)
            - E-mail de contato
            - Telefone de contato
            
            Se alguma informação de contato NÃO for encontrada, retorne uma string vazia '' para o campo correspondente.
            
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

        # Clean the JSON
        import json
        cleaned_results = {}
        for candidate_key, response_text in final_results.items():
            try:
                cleaned_results[candidate_key] = json.loads(response_text)
            except json.JSONDecodeError:
                cleaned_results[candidate_key] = {"error": "Falha ao ler o veredito da IA", "texto_bruto": response_text}

        yield {"status": "success", "results": cleaned_results, "message": "Análises concluídas com sucesso!"}