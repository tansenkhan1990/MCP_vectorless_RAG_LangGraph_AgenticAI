"""
RAG uploader — extracts text from PDFs and ingests chunks into Supabase.
"""

import logging
from pathlib import Path

import fitz  # PyMuPDF

from app.db import get_supabase_client

logger = logging.getLogger(__name__)

_DEFAULT_CHUNK_SIZE = 1200
_CHUNK_OVERLAP = 200  # overlap helps preserve context across chunk boundaries


def chunk_text(text: str, size: int = _DEFAULT_CHUNK_SIZE, overlap: int = _CHUNK_OVERLAP) -> list[str]:
    """
    Split *text* into chunks of approximately *size* characters with *overlap*.

    Args:
        text: The source text to chunk.
        size: Maximum chunk size in characters.
        overlap: Number of overlapping characters between consecutive chunks.

    Returns:
        A list of text chunks.
    """
    if not text.strip():
        return []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap  # slide back by overlap amount

    return chunks


def ingest_pdf(file_path: str, filename: str) -> str:
    """
    Extract text from a PDF, chunk it, and insert into Supabase.

    Args:
        file_path: Path to the PDF file on disk.
        filename: Original filename (stored as metadata).

    Returns:
        A success message with the count of inserted chunks.

    Raises:
        FileNotFoundError: If the file does not exist.
        Exception: On Supabase insert failure.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    client = get_supabase_client()
    doc = fitz.open(file_path)
    total_chunks = 0

    try:
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            if not text.strip():
                logger.debug("Skipping empty page %d in %s", page_num, filename)
                continue

            chunks = chunk_text(text)

            for chunk in chunks:
                client.table("private_company_details").insert({
                    "file_name": filename,
                    "title": filename,
                    "page_number": page_num,
                    "chunk_text": chunk,
                    "category": "private",
                    "source": "uploaded_pdf",
                }).execute()
                total_chunks += 1

        logger.info(
            "Ingested %d chunks from %d pages of '%s'",
            total_chunks, len(doc), filename,
        )
        return f"PDF uploaded successfully — {total_chunks} chunks ingested from {len(doc)} pages."

    finally:
        doc.close()