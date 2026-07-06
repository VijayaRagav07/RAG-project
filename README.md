# Simple-RAG Playground

A modular, highly polished Retrieval-Augmented Generation (RAG) platform built with Streamlit, FAISS, and Gemini/Ollama. This application allows you to index local PDF documents, query them, and get synthesized answers with direct source page citations.

## 🚀 Features

- **Double-Agent Providers**: Supports cloud-based **Google Gemini** (via Gemini API) and local-offline **Ollama** models.
- **Glassmorphic UI**: Customized modern styling featuring CSS gradients, visual indicators, side-by-side columns, and a dedicated retrieved context inspector.
- **Pure Python Chunking**: Implementing an overlap-aware recursive text splitter from scratch for ultimate performance transparency.
- **Resilient Vector Store**: Wraps FAISS Inner-Product similarity indexing, and features a bulletproof **Numpy-based fallback** vector search engine if FAISS compilation isn't available on the host machine.
- **Token-by-Token Streaming**: Streams generated tokens dynamically into the chat interface for a premium UX.

---

## 📁 File Structure

```
Simple-RAG/
│
├── app.py                  # Streamlit UI with custom CSS styles
├── config.py               # Path configurations and model parameters
├── requirements.txt        # Package dependencies
├── .env                    # Gemini API key configuration
├── README.md               # Setup and usage instructions
│
├── core/
│   ├── pdf_loader.py       # Extract text from pages of a PDF
│   ├── text_splitter.py    # Custom overlap-aware recursive splitter
│   ├── embeddings.py       # Embedding generation for Gemini/Ollama/Mock
│   ├── vector_store.py     # FAISS vector database wrapper with Numpy fallback
│   ├── retriever.py        # Similarity context fetcher
│   ├── llm.py              # Gemini & Ollama synchronous/streaming connectors
│   └── rag_pipeline.py     # End-to-end RAG orchestrator
│
├── utils/
│   └── helpers.py          # Custom CSS stylesheets injection
│
└── data/                   # Automatically created runtime directories
    ├── uploads/            # Uploaded PDF cache
    └── faiss_index/        # Vector index storage
```

---

## 🛠️ Setup Instructions

### 1. Clone/Open the Workspace
Ensure your shell is positioned in the project directory:
```bash
cd "c:/Users/hp/Documents/RAG project"
```

### 2. Install Dependencies
It's recommended to use a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 3. Configure API Keys (Optional but Recommended)
Open the `.env` file and insert your Gemini API Key:
```env
GEMINI_API_KEY=AIzaSy...
```
*(Alternatively, you can paste the API Key directly in the UI sidebar when running.)*

---

## ⚡ Run the Application

Start the Streamlit development server:
```bash
streamlit run app.py
```
This will open the application in your browser, typically at `http://localhost:8501`.

---

## 🔍 How it Works
1. **Document Loading**: The PDF is parsed page-by-page by `pypdf`, extracting raw text along with source filename and page numbers.
2. **Text Chunking**: Text is split recursively on characters `\n\n`, `\n`, ` ` and `""` to produce segments within `chunk_size` while keeping some `chunk_overlap` to maintain narrative context.
3. **Embedding Generation**: The text chunks are mapped to 768-dimensional dense vectors using Gemini's `text-embedding-004` (or Ollama's local embeddings).
4. **Indexing**: Chunks and vectors are registered in the vector store. The vector store normalizes the vectors and registers them in a FAISS inner-product index.
5. **Retrieval**: When you submit a question, the query is embedded, and the vector index computes the top $K$ most similar paragraphs.
6. **Prompt Assembly**: The retrieved text chunks are injected as reference context into a system prompt.
7. **Synthesis**: The LLM synthesizes an answer referencing the context, streaming it token-by-token directly to your chat interface.
