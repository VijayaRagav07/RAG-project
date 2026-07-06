import os
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("Warning: faiss-cpu is not installed or could not be loaded. Using Numpy-based fallback vector store.")

class VectorStore:
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.documents = []  # List of Dict[str, Any] with 'text' and 'metadata'
        self.vectors = []    # List of List[float] for numpy fallback
        self.index = None
        self.use_faiss = FAISS_AVAILABLE
        
        self._init_index()

    def _init_index(self):
        """Initializes the FAISS index if available."""
        if self.use_faiss:
            # We use Inner Product (IP) search. 
            # If we normalize vectors, this is equivalent to cosine similarity.
            self.index = faiss.IndexFlatIP(self.dimension)
        else:
            self.index = None

    def _normalize_vector(self, v: List[float]) -> np.ndarray:
        """Normalizes a single vector to unit length."""
        arr = np.array(v, dtype=np.float32)
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm
        return arr

    def add_documents(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Adds text chunks and their embeddings to the vector store.
        Each chunk is a dictionary: {"text": "...", "metadata": {...}}
        """
        if not chunks:
            return
        
        assert len(chunks) == len(embeddings), "Number of chunks must match number of embeddings."
        
        # Check and set dimension based on incoming embedding if needed
        if len(embeddings) > 0 and len(embeddings[0]) != self.dimension:
            self.dimension = len(embeddings[0])
            self._init_index()

        normalized_vectors = []
        for chunk, emb in zip(chunks, embeddings):
            # Normalize vector for cosine similarity
            norm_v = self._normalize_vector(emb)
            normalized_vectors.append(norm_v)
            self.documents.append(chunk)
            self.vectors.append(norm_v.tolist())

        if self.use_faiss:
            vectors_np = np.vstack(normalized_vectors).astype(np.float32)
            self.index.add(vectors_np)

    def search(self, query_embedding: List[float], k: int = 4) -> List[Tuple[Dict[str, Any], float]]:
        """
        Searches for the k most similar chunks to the query embedding.
        Returns:
            List[Tuple[Dict[str, Any], float]]: List of tuples containing (document, similarity_score).
        """
        if not self.documents:
            return []

        # Ensure k does not exceed number of documents
        k = min(k, len(self.documents))
        if k <= 0:
            return []

        query_v = self._normalize_vector(query_embedding).astype(np.float32)

        if self.use_faiss:
            # Reshape query to 2D array: (1, dimension)
            query_np = query_v.reshape(1, -1)
            # D = distances (inner product, i.e., similarity score since normalized)
            # I = indices of matching vectors
            D, I = self.index.search(query_np, k)
            
            results = []
            for score, idx in zip(D[0], I[0]):
                if idx != -1 and idx < len(self.documents):
                    results.append((self.documents[idx], float(score)))
            return results
        else:
            # Numpy fallback similarity search (Cosine similarity via dot product of normalized vectors)
            vectors_np = np.vstack(self.vectors).astype(np.float32)
            # Shape of vectors_np: (num_docs, dimension)
            # Shape of query_v: (dimension,)
            similarities = np.dot(vectors_np, query_v)
            
            # Get indices of top k largest values
            top_k_idx = np.argsort(similarities)[::-1][:k]
            
            results = []
            for idx in top_k_idx:
                results.append((self.documents[idx], float(similarities[idx])))
            return results

    def save(self, directory_path: str):
        """Saves the vector index and document database to a directory."""
        dir_path = Path(directory_path)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Save documents metadata & text
        docs_file = dir_path / "documents.pkl"
        with open(docs_file, "wb") as f:
            pickle.dump(self.documents, f)
            
        # Save raw normalized vectors (useful for fallback or rebuilding)
        vectors_file = dir_path / "vectors.npy"
        np.save(vectors_file, np.array(self.vectors, dtype=np.float32))

        # Save index config details
        config_file = dir_path / "index_config.json"
        with open(config_file, "w") as f:
            json.dump({
                "dimension": self.dimension,
                "use_faiss": self.use_faiss
            }, f)

        # Save FAISS index
        if self.use_faiss and self.index is not None:
            faiss_file = dir_path / "index.faiss"
            faiss.write_index(self.index, str(faiss_file))

    def load(self, directory_path: str):
        """Loads the vector index and document database from a directory."""
        dir_path = Path(directory_path)
        if not dir_path.exists():
            raise FileNotFoundError(f"Index directory does not exist: {directory_path}")
            
        docs_file = dir_path / "documents.pkl"
        if not docs_file.exists():
            raise FileNotFoundError(f"Documents file missing in: {directory_path}")
            
        with open(docs_file, "rb") as f:
            self.documents = pickle.load(f)
            
        # Load index config
        config_file = dir_path / "index_config.json"
        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)
                self.dimension = config.get("dimension", self.dimension)
                
        # Load raw vectors
        vectors_file = dir_path / "vectors.npy"
        if vectors_file.exists():
            self.vectors = np.load(vectors_file).tolist()
        else:
            self.vectors = []

        # Load FAISS index if available and requested
        faiss_file = dir_path / "index.faiss"
        if self.use_faiss and faiss_file.exists():
            self.index = faiss.read_index(str(faiss_file))
        else:
            # Fall back to rebuilding index from raw vectors or using numpy fallback
            self._init_index()
            if self.use_faiss and self.vectors:
                vectors_np = np.array(self.vectors, dtype=np.float32)
                self.index.add(vectors_np)

    def clear(self):
        """Clears the vector store."""
        self.documents = []
        self.vectors = []
        self._init_index()
