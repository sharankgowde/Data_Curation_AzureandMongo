from typing import List
import fitz  # pymupdf


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes using PyMuPDF (fitz)."""
    text_chunks: List[str] = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            page_text = page.get_text("text")
            if page_text:
                text_chunks.append(page_text)
    return "\n".join(text_chunks)


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    """Simple character-based chunking with overlap.

    Returns list of text chunks.
    """
    if not text:
        return []
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
    return chunks
