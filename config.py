import os
from pathlib import Path

# Base workspace directory
BASE_DIR = Path(__file__).resolve().parent

# Data directories
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
INDEX_DIR = DATA_DIR / "faiss_index"

# Create directories if they do not exist
for directory in [DATA_DIR, UPLOAD_DIR, INDEX_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Default LLM configurations
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"
DEFAULT_EMBEDDING_MODEL = "models/gemini-embedding-2"

# Default Chunking & Retrieval Configurations
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_TOP_K = 4

# Ollama local endpoint
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_OLLAMA_LLM = "llama3"
DEFAULT_OLLAMA_EMBED = "nomic-embed-text"
