"""
Document text extraction utilities (PDF + plain text).
"""

from pathlib import Path
from typing import Optional
import io

from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF using pypdf. Falls back gracefully."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text)
        return "\n\n".join(pages).strip()
    except Exception as e:
        return f"[PDF extraction error: {str(e)}]"


def extract_text_from_upload(filename: str, file_bytes: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    # Treat everything else as UTF-8 text
    try:
        return file_bytes.decode("utf-8", errors="replace")
    except Exception:
        return file_bytes.decode("latin-1", errors="replace")
