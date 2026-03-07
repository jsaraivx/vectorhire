from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any


from .database import engine, ResumeChunkModel


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class VectorRepository:
    def __init__(self):
        self.session_factory = SessionLocal

    def upsert_chunks(self, prepared_data: List[Dict[str, Any]]):
        """
        Inserts or updates resume chunks and their embeddings into PostgreSQL.
        """
        with self.session_factory() as session:
            try:
                for item in prepared_data:
                    chunk = ResumeChunkModel(
                        id=item["id"],
                        file_name=item["metadata"]["file_name"],
                        text_content=item["metadata"]["text"],
                        embedding=item["values"]
                    )
                    session.merge(chunk)  # merge handles upsert logic based on primary key
                session.commit()
            except Exception as e:
                session.rollback()
                raise e

    def search_similar_chunks(self, query_embedding: List[float], limit: int = 5):
        """
        Performs a vector similarity search using cosine distance.
        """
        with self.session_factory() as session:
            results = session.query(ResumeChunkModel).order_by(
                ResumeChunkModel.embedding.cosine_distance(query_embedding)
            ).limit(limit).all()
            return results
