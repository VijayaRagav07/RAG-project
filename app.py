import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

import config
from core.rag_pipeline import RAGPipeline
from utils.helpers import inject_styles

# Set Page Config
st.set_page_config(
    page_title="Simple-RAG Playground",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS styles for glassmorphism dark theme
inject_styles()

# Define sidebar header
st.sidebar.markdown("## ⚙️ Configuration")

# Model Provider
provider = st.sidebar.selectbox(
    "LLM & Embedding Provider",
    options=["Gemini", "Ollama"],
    index=0,
    help="Select whether to use cloud-based Gemini or locally-hosted Ollama."
)

# API Key or URL Settings
api_key = None
ollama_url = config.DEFAULT_OLLAMA_URL
llm_model = ""
embedding_model = ""

if provider == "Gemini":
    # Check for API Key in environment
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.sidebar.text_input(
        "Gemini API Key",
        value=env_api_key if env_api_key else "",
        type="password",
        placeholder="Enter your Gemini API key...",
        help="Get a key from https://aistudio.google.com/"
    )
    # Use input if provided, otherwise fallback
    api_key = api_key_input if api_key_input.strip() else None
    
    llm_model = st.sidebar.selectbox(
        "Gemini LLM Model",
        options=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash", "gemini-2.5-flash"],
        index=0
    )
    embedding_model = config.DEFAULT_EMBEDDING_MODEL
else:
    ollama_url = st.sidebar.text_input(
        "Ollama URL",
        value=config.DEFAULT_OLLAMA_URL
    )
    llm_model = st.sidebar.text_input(
        "Ollama LLM Model Name",
        value=config.DEFAULT_OLLAMA_LLM,
        help="Make sure the model is pulled locally (e.g., 'llama3', 'mistral')"
    )
    embedding_model = st.sidebar.text_input(
        "Ollama Embedding Model Name",
        value=config.DEFAULT_OLLAMA_EMBED,
        help="Make sure the embedding model is pulled (e.g., 'nomic-embed-text')"
    )

# Advanced Settings Expander
with st.sidebar.expander("🛠️ Advanced Settings", expanded=False):
    chunk_size = st.slider("Chunk Size (characters)", 200, 2000, config.DEFAULT_CHUNK_SIZE, 100)
    chunk_overlap = st.slider("Chunk Overlap (characters)", 50, 500, config.DEFAULT_CHUNK_OVERLAP, 50)
    top_k = st.slider("Retrieval Top-K Chunks", 1, 10, config.DEFAULT_TOP_K, 1)
    temperature = st.slider("LLM Temperature", 0.0, 1.0, 0.3, 0.1)

# Initialize/re-initialize the RAG Pipeline in session state
pipeline_key = f"{provider}_{api_key}_{llm_model}_{embedding_model}_{ollama_url}"
if "pipeline_key" not in st.session_state or st.session_state.pipeline_key != pipeline_key:
    st.session_state.pipeline = RAGPipeline(
        provider=provider,
        api_key=api_key,
        llm_model=llm_model,
        embedding_model=embedding_model,
        ollama_url=ollama_url
    )
    st.session_state.pipeline_key = pipeline_key

# Document Management Section in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📄 Document Upload")

uploaded_file = st.sidebar.file_uploader("Upload PDF Document", type=["pdf"])

if uploaded_file is not None:
    if st.sidebar.button("⚡ Index Document"):
        with st.spinner("Extracting, chunking and embedding PDF..."):
            try:
                # Save file to uploads folder
                file_path = config.UPLOAD_DIR / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Index PDF in pipeline
                num_chunks = st.session_state.pipeline.index_pdf(
                    str(file_path),
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
                st.sidebar.success(f"Success! Indexed {num_chunks} chunks.")
                # Force refresh
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Failed to index PDF: {e}")

# Display Indexed Documents
st.sidebar.markdown("### 📚 Indexed Documents")
indexed_docs = st.session_state.pipeline.get_indexed_documents()

if indexed_docs:
    for doc in indexed_docs:
        st.sidebar.markdown(f'<span class="pill-badge-green">✓ {doc}</span>', unsafe_allow_html=True)
        
    st.sidebar.markdown(" ")
    if st.sidebar.button("🗑️ Clear Vector Index", help="Delete all files in database"):
        st.session_state.pipeline.clear_index()
        st.session_state.messages = []
        st.sidebar.info("Index wiped and chat history reset.")
        st.rerun()
else:
    st.sidebar.info("No documents uploaded yet.")


# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main Workspace Header
st.markdown(
    '<div class="premium-header">'
    '<h1 class="gradient-title">Simple-RAG Playground</h1>'
    '<p class="subtitle">A modular Retrieval-Augmented Generation platform powered by Gemini & FAISS</p>'
    '</div>',
    unsafe_allow_html=True
)

# Grid Layout: Left for Chat, Right for context viewer
chat_col, source_col = st.columns([1.6, 1.0], gap="large")

with chat_col:
    # Header area inside chat column to align the Clear Chat button
    chat_header_left, chat_header_right = st.columns([4, 1])
    with chat_header_left:
        st.subheader("💬 Interactive Assistant")
    with chat_header_right:
        if st.button("🧹 Clear Chat"):
            st.session_state.messages = []
            st.rerun()
            
    # Check if we have indexed documents
    has_docs = st.session_state.pipeline.check_has_index()
    
    if not has_docs:
        st.markdown(
            '<div class="glass-panel">'
            '<h4>🚀 Getting Started</h4>'
            '<p>Welcome to the Simple-RAG application! To begin conversing with your documents:</p>'
            '<ol>'
            '<li>Provide a <b>Gemini API Key</b> in the sidebar (or run <b>Ollama</b> locally).</li>'
            '<li>Upload a <b>PDF</b> file in the sidebar.</li>'
            '<li>Click the <b>⚡ Index Document</b> button to extract and vector-index the content.</li>'
            '<li>Ask questions in the chat window below!</li>'
            '</ol>'
            '</div>',
            unsafe_allow_html=True
        )
        
    # Render chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Process user input
    if prompt := st.chat_input("Ask a question about the indexed documents...", disabled=not has_docs):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display assistant message
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            with st.spinner("Retrieving relevant context & synthesizing response..."):
                try:
                    # Query pipeline in streaming mode
                    stream_gen, retrieved_chunks = st.session_state.pipeline.query_stream(
                        prompt,
                        top_k=top_k,
                        temperature=temperature
                    )
                    
                    # Stream tokens to UI
                    full_response = ""
                    # st.write_stream takes a generator and writes tokens in real-time
                    # Since write_stream handles writing, we use it directly on the stream_gen
                    full_response = response_placeholder.write_stream(stream_gen)
                    
                    # Store assistant message in history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response,
                        "citations": retrieved_chunks
                    })
                    
                    # Store current search citations in session state to display in the right column
                    st.session_state.last_citations = retrieved_chunks
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error generating answer: {e}")

with source_col:
    st.subheader("🔍 Retrieved Context")
    
    # Display details of the last query's citations
    citations = st.session_state.get("last_citations", [])
    
    if not has_docs:
        st.markdown(
            '<div class="glass-panel" style="text-align: center;">'
            '<p style="color: #64748b; margin: 0;">Upload a document to see source citations here.</p>'
            '</div>',
            unsafe_allow_html=True
        )
    elif not citations:
        # Check if we have any messages, if yes, it means we did a query but retrieved nothing (unlikely unless empty db)
        if st.session_state.messages:
            st.markdown(
                '<div class="glass-panel" style="text-align: center;">'
                '<p style="color: #64748b; margin: 0;">No matching context retrieved for the last question.</p>'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="glass-panel" style="text-align: center;">'
                '<p style="color: #64748b; margin: 0;">Ask a question in the chat to view retrieved sources and similarity scores in real-time.</p>'
                '</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown(f"Found **{len(citations)}** relevant passages:")
        for idx, chunk in enumerate(citations):
            meta = chunk["metadata"]
            score = chunk["score"]
            text = chunk["text"]
            
            # Format similarity score as percentage
            score_percent = f"{score * 100:.1f}%" if score <= 1.0 else f"{score:.2f}"
            
            st.markdown(
                f'<div class="citation-card">'
                f'  <div class="citation-header">'
                f'    <span>📄 {meta.get("source", "Unknown")} (Pg {meta.get("page_number", "N/A")})</span>'
                f'    <span class="pill-badge" style="margin:0;">Sim: {score_percent}</span>'
                f'  </div>'
                f'  <div class="citation-text">"{text}"</div>'
                f'</div>',
                unsafe_allow_html=True
            )
