import streamlit as st

def get_custom_css() -> str:
    """
    Returns custom CSS code designed to inject a high-end, premium,
    glassmorphic dark look into the Streamlit application.
    """
    return """
    <style>
    /* Import modern font from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Apply font to Streamlit elements */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Background Gradient for the Entire App Workspace */
    .stApp {
        background: radial-gradient(circle at top left, #121829 0%, #0a0b10 100%) !important;
        color: #e2e8f0 !important;
    }
    
    /* Custom Glassmorphic Cards & Layout Headers */
    .premium-header {
        text-align: center;
        padding: 1.5rem 0 2rem 0;
    }
    
    .gradient-title {
        background: linear-gradient(135deg, #a78bfa 0%, #3b82f6 50%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -0.06rem;
        margin-bottom: 0.4rem;
        display: inline-block;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.15rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    /* Custom Sidebar Aesthetics */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.7) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2, 
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: #f8fafc;
        font-weight: 700;
        letter-spacing: -0.02rem;
    }
    
    /* Modern Glass Container Panel */
    .glass-panel {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        backdrop-filter: blur(8px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
    }
    
    /* Styled tags/pill badges */
    .pill-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .pill-badge-green {
        display: inline-flex;
        align-items: center;
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Custom citation boxes */
    .citation-card {
        background: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #6366f1;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 0.75rem;
        margin-bottom: 0.75rem;
        border-top: 1px solid rgba(255, 255, 255, 0.03);
        border-right: 1px solid rgba(255, 255, 255, 0.03);
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    }
    
    .citation-header {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        color: #818cf8;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .citation-text {
        font-size: 0.9rem;
        color: #94a3b8;
        line-height: 1.5;
        font-style: italic;
    }
    
    /* Custom style for primary actions & standard Streamlit buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #3b82f6 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1.25rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.3) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.45) !important;
        background: linear-gradient(135deg, #4f46e5 0%, #2563eb 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Status panel colors */
    .custom-status-success {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #a7f3d0;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        font-size: 0.875rem;
        margin-bottom: 1rem;
    }
    
    .custom-status-info {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: #bfdbfe;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        font-size: 0.875rem;
        margin-bottom: 1rem;
    }
    </style>
    """

def inject_styles():
    """Helper function to run styling injection inside app.py."""
    st.markdown(get_custom_css(), unsafe_allow_html=True)
