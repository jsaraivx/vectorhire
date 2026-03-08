from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any


class EmbeddingService:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the local model. On the first run, it will 
        download the model weights (approximately 80MB) to your machine.
        """
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, chunks: List[Any]) -> List[Dict[str, Any]]:
        """
        Generates vectors and prepares the exact payload expected by Pinecone.
        """
        
        prepared_data = []

        # Extract text content from the chunk objects
        text_list = [chunk.text_content for chunk in chunks]   

        # Create the vector representations
        embeddings = self.model.encode(text_list)

        for chunk, vector in zip(chunks, embeddings):
            payload = {
                "id": chunk.chunk_id,
                "values": vector.tolist(), # Convert numpy array to list for JSON compatibility
                "metadata": {
                    "session_id": chunk.session_id,
                    "file_name": chunk.file_name,
                    "text": chunk.text_content
                }
            }
            prepared_data.append(payload)

        return prepared_data