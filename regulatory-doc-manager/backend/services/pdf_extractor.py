"""
PDF text extraction using PyMuPDF (fitz).
Fast, no external services needed. Handles most regulatory PDFs well.
Falls back gracefully on scanned / image-only PDFs.
"""
import fitz  # PyMuPDF
import io


def extract_text(file_bytes: bytes) -> tuple[str, int]:
    """
    Returns (full_text, page_count).
    Text is extracted page-by-page and joined with newlines.
    """
    doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
    pages = []
    for page in doc:
        text = page.get_text("text")
        if text.strip():
            pages.append(text)
    doc.close()
    full_text = "\n\n".join(pages)
    return full_text, len(pages)
