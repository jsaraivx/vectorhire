import os
import google.generativeai as genai
from pydantic import BaseModel, Field

from dotenv import load_dotenv
from src.vector_db.embedding_service import EmbeddingService
from src.vector_db.repository import VectorRepository

load_dotenv()


# 1. Definimos EXATAMENTE como queremos que a IA responda
class AvaliacaoCandidato(BaseModel):
    score_aderencia: int = Field(description="Nota de 0 a 100 baseada no match entre currículo e vaga")
    decisao: str = Field(description="DEVE SER EXATAMENTE: 'Aprovado para Entrevista' ou 'Reprovado'")
    justificativa_tecnica: str = Field(description="Explicação detalhada do porquê da nota, citando tecnologias do currículo.")


class MatchingService:
    def __init__(self):
        # Inicializa as conexões
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não encontrada no .env")
            
        genai.configure(api_key=api_key)
        
        # O Gemini 1.5 Flash é perfeito para tarefas rápidas de RAG
        self.llm = genai.GenerativeModel('gemini-2.5-flash')
        
        # Instancia seus motores locais
        self.embedding_service = EmbeddingService()
        self.db = VectorRepository()

    def avaliar_candidato_para_vaga(self, job_description: str) -> str:
        """
        Orquestra o RAG: Vetoriza a vaga, busca no banco, e pede pro LLM avaliar.
        """
        print("🤖 [1/4] Vetorizando a Descrição da Vaga...")
        # TODO: Use o seu self.embedding_service.model.encode() para gerar o vetor da string 'job_description'
        # Dica: O modelo encode espera uma lista de textos, então passe [job_description]. 
        # Depois, extraia o vetor e converta para lista nativa do Python com .tolist()
        jd_vector = [] 
        resultado_final = {}

        emb_jd = self.embedding_service.model.encode(job_description)

        jd_vector = emb_jd.tolist()

        print(job_description)
        # print(jd_vector)

        print("🔍 [2/4] Buscando os fragmentos de currículo mais relevantes no Postgres...")
        # TODO: Use o seu self.db.search_similar_chunks() passando o jd_vector. 
        # Peça os top 5 resultados.
        
        chunk_pescaria = self.db.search_similar_chunks(jd_vector, 15)

        unique_candidates = set([c.file_name for c in chunk_pescaria])
        print(f"🎯 Candidatos encontrados no radar: {unique_candidates}")

        # chunks_relevantes = self.db.search_similar_chunks(jd_vector, 5)

        for candidate in unique_candidates:
            print(f"Analisando candidato {candidate}..")

            print("🧠 [3/4] Montando o contexto para o LLM...")
            # TODO: Crie uma string única juntando o texto (text_content) dos chunks encontrados.

            candidate_chunks = self.db.get_chunk_file_by_name(candidate)

            contexto_curriculo = f"\n\n".join(
                [c.text_content for c in candidate_chunks]
            )

            # print(contexto_curriculo)
            
            print("⚡ [4/4] Consultando o Gemini 1.5 Flash...")
            
            # O Prompt de Sistema define as regras do jogo
            prompt = f"""
            Você é um Tech Recruiter Sênior super rigoroso.
            Sua missão é avaliar se o candidato atende aos requisitos da vaga abaixo, 
            baseando-se ÚNICA E EXCLUSIVAMENTE nos fragmentos de currículo fornecidos.
            
            DESCRIÇÃO DA VAGA (Requisitos):
            {job_description}
            
            FRAGMENTOS DO CURRÍCULO DO CANDIDATO:
            {contexto_curriculo}
            
            Siga estritamente o formato JSON solicitado, avaliando a aderência técnica.
            """

            # Chamada da API forçando a saída estruturada usando o schema do Pydantic
            response = self.llm.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=AvaliacaoCandidato,
                    temperature=0.1 # Temperatura baixa = menos criatividade, mais precisão analítica
                )
            )

            resultado_final[candidate] = response.text


        # print(response,  '\n')

        return resultado_final