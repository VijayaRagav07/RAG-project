import os
import google.generativeai as genai
import requests
import numpy as np
from typing import List

class EmbeddingGenerator:
    def __init__(self, provider: str = "gemini", api_key: str = None, model: str = None, ollama_url: str = None):
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.ollama_url = ollama_url or "http://localhost:11434"
        
        if self.provider == "gemini":
            if self.api_key:
                genai.configure(api_key=self.api_key)
            self.model = model or "models/gemini-embedding-2"
        elif self.provider == "ollama":
            self.model = model or "nomic-embed-text"
        else:
            # Fallback mock/local logic if needed
            self.model = "mock"

    def get_embedding(self, text: str) -> List[float]:
        """Generates embedding for a single text block."""
        if not text.strip():
            # Return empty or dummy vector
            return [0.0] * (3072 if self.provider == "gemini" else 384)

        if self.provider == "gemini":
            if not self.api_key:
                raise ValueError("Gemini API Key is not set. Please provide it in the sidebar or a .env file.")
            try:
                response = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="retrieval_query" if len(text) < 200 else "retrieval_document"
                )
                return response['embedding']
            except Exception as e:
                print(f"Error generating Gemini embedding: {e}")
                raise e
                
        elif self.provider == "ollama":
            try:
                response = requests.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                    timeout=10
                )
                response.raise_for_status()
                return response.json()["embedding"]
            except Exception as e:
                print(f"Error generating Ollama embedding: {e}")
                raise e
                
        elif self.provider == "mock":
            # Generate deterministic mock embeddings based on text hash for offline testing
            state = np.random.RandomState(abs(hash(text)) % (2**32))
            vector = state.randn(768)
            norm = np.linalg.norm(vector)
            vector = vector / norm if norm > 0 else vector
            return vector.tolist()
            
        else:
            raise ValueError(f"Unknown embedding provider: {self.provider}")

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of text blocks."""
        if not texts:
            return []

        if self.provider == "gemini":
            if not self.api_key:
                raise ValueError("Gemini API Key is not set. Please provide it in the sidebar or a .env file.")
            try:
                # Gemini supports batch embeddings
                response = genai.embed_content(
                    model=self.model,
                    content=texts,
                    task_type="retrieval_document"
                )
                # Check response format
                if 'embedding' in response:
                    return response['embedding']
                else:
                    # Fallback to itemized if format is unexpected
                    return [self.get_embedding(t) for t in texts]
            except Exception as e:
                print(f"Batch embedding failed, falling back to individual: {e}")
                return [self.get_embedding(t) for t in texts]
        else:
            # Ollama does not natively support batch embedding in a simple API call on older versions
            return [self.get_embedding(t) for t in texts]
