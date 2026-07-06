import os
from pathlib import Path
from typing import List, Dict, Any, Generator, Tuple

import config
from core.pdf_loader import load_pdf
from core.text_splitter import RecursiveTextSplitter
from core.embeddings import EmbeddingGenerator
from core.vector_store import VectorStore
from core.retriever import Retriever
from core.llm import LLMInterface

class RAGPipeline:
    def __init__(self, provider: str = "gemini", api_key: str = None, 
                 llm_model: str = None, embedding_model: str = None,
                 ollama_url: str = None):
        self.provider = provider
        self.api_key = api_key
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.ollama_url = ollama_url
        
        # Initialize Embeddings and Vector Store
        self.embeddings = EmbeddingGenerator(
            provider=provider,
            api_key=api_key,
            model=embedding_model,
            ollama_url=ollama_url
        )
        
        # We will initialize a default vector store dimension.
        # Gemini embedding-2 dimension is 3072. Ollama nomic embedding dimension is 768.
        # Dimension is dynamically set by the actual embeddings returned.
        self.vector_store = VectorStore(dimension=3072)
        self.retriever = Retriever(self.vector_store, self.embeddings)
        
        # Initialize LLM
        self.llm = LLMInterface(
            provider=provider,
            api_key=api_key,
            model=llm_model,
            ollama_url=ollama_url
        )
        
        # Load index if it already exists
        self.load_index_if_exists()

    def load_index_if_exists(self) -> bool:
        """Attempts to load a previously saved index from the config directory."""
        try:
            if (config.INDEX_DIR / "documents.pkl").exists():
                self.vector_store.load(str(config.INDEX_DIR))
                return True
        except Exception as e:
            print(f"Could not load vector index: {e}")
        return False

    def check_has_index(self) -> bool:
        """Returns True if there are indexed documents present."""
        return len(self.vector_store.documents) > 0

    def get_indexed_documents(self) -> List[str]:
        """Returns a list of unique filenames that have been indexed."""
        seen = set()
        for doc in self.vector_store.documents:
            seen.add(doc["metadata"]["source"])
        return sorted(list(seen))

    def clear_index(self):
        """Clears the current vector store and deletes saved files from disk."""
        self.vector_store.clear()
        for filename in ["documents.pkl", "vectors.npy", "index_config.json", "index.faiss"]:
            file_path = config.INDEX_DIR / filename
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as e:
                    print(f"Error removing index file {file_path}: {e}")

    def index_pdf(self, pdf_path: str, chunk_size: int, chunk_overlap: int) -> int:
        """
        Loads, splits, embeds, and indexes a PDF file.
        Saves the resulting index to disk.
        Returns:
            int: Number of chunks added.
        """
        # Load pages from PDF
        pages = load_pdf(pdf_path)
        if not pages:
            raise ValueError("No text could be extracted from this PDF.")
            
        # Split text into chunks
        splitter = RecursiveTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = splitter.split_documents(pages)
        
        # Generate embeddings
        texts = [chunk["text"] for chunk in chunks]
        embeddings_list = self.embeddings.get_embeddings(texts)
        
        # Add to vector store
        self.vector_store.add_documents(chunks, embeddings_list)
        
        # Save vector store to disk
        self.vector_store.save(str(config.INDEX_DIR))
        
        return len(chunks)

    def _build_rag_prompt(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Constructs the prompt containing query and retrieved context."""
        context_str_list = []
        for i, chunk in enumerate(retrieved_chunks):
            meta = chunk["metadata"]
            source_info = f"[Source {i+1}: {meta.get('source', 'Unknown')} | Page {meta.get('page_number', 'N/A')} | Similarity: {chunk.get('score', 0):.2f}]"
            context_str_list.append(f"{source_info}\n{chunk['text']}")
            
        context = "\n\n".join(context_str_list)
        
        prompt = f"""You are a helpful, professional assistant answering questions based on the provided context retrieved from PDF documents.
Answer the user's question as accurately, honestly, and concisely as possible using ONLY the context provided below.
When referencing details, you may cite the source and page number from the context headings (e.g. "[Source 1, Page 2]").
If the answer cannot be found in the context, state clearly that you do not know based on the provided documents. Do not make up information.

Context:
---
{context}
---

User Question: {query}

Answer:"""
        return prompt

    def query(self, query_text: str, top_k: int = 4, temperature: float = 0.3) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Retrieves matching chunks, builds prompt, and fetches synchronous LLM response.
        Returns:
            Tuple[str, List[Dict[str, Any]]]: (LLM response string, retrieved chunks with metadata).
        """
        retrieved_chunks = self.retriever.retrieve(query_text, k=top_k)
        if not retrieved_chunks:
            return "No relevant context found. Please index some documents first.", []
            
        prompt = self._build_rag_prompt(query_text, retrieved_chunks)
        response = self.llm.generate_response(prompt, temperature=temperature)
        return response, retrieved_chunks

    def query_stream(self, query_text: str, top_k: int = 4, temperature: float = 0.3) -> Tuple[Generator[str, None, None], List[Dict[str, Any]]]:
        """
        Retrieves matching chunks, builds prompt, and returns a generator streaming LLM response tokens.
        Returns:
            Tuple[Generator[str, None, None], List[Dict[str, Any]]]: (Token generator, retrieved chunks with metadata).
        """
        retrieved_chunks = self.retriever.retrieve(query_text, k=top_k)
        if not retrieved_chunks:
            # Return a simple generator that yields a warning
            def empty_gen():
                yield "No relevant context found. Please upload and index documents first."
            return empty_gen(), []
            
        prompt = self._build_rag_prompt(query_text, retrieved_chunks)
        stream_generator = self.llm.generate_response_stream(prompt, temperature=temperature)
        return stream_generator, retrieved_chunks
