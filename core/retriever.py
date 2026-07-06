from typing import List, Dict, Any
from core.vector_store import VectorStore
from core.embeddings import EmbeddingGenerator

class Retriever:
    def __init__(self, vector_store: VectorStore, embedding_generator: EmbeddingGenerator):
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator

    def retrieve(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        Takes a text query, embeds it, retrieves the top k matching document chunks
        from the VectorStore, and returns them formatted with their similarity scores.
        """
        if not query.strip():
            return []

        # Embed query
        query_embedding = self.embedding_generator.get_embedding(query)
        
        # Perform vector search
        search_results = self.vector_store.search(query_embedding, k=k)
        
        # Format retrieval output
        retrieved_chunks = []
        for doc, score in search_results:
            retrieved_chunks.append({
                "text": doc["text"],
                "metadata": doc["metadata"],
                "score": score
            })
            
        return retrieved_chunks
