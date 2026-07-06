import pypdf
from pathlib import Path
from typing import List, Dict, Any

def load_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Reads text content from a PDF file using pypdf and tracks metadata.
    Returns:
        List[Dict[str, Any]]: List of pages containing 'text' and 'metadata' (page_num, source).
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found at: {file_path}")

    pages_data = []
    try:
        reader = pypdf.PdfReader(path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                pages_data.append({
                    "text": text,
                    "metadata": {
                        "source": path.name,
                        "page_number": i + 1  # 1-based indexing for display
                    }
                })
    except Exception as e:
        print(f"Error loading PDF {file_path}: {e}")
        raise e

    return pages_data
