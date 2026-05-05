"""
PDF service — handles PDF upload and ingestion.

Handles:
  - File validation (type, size, magic bytes)
  - File storage
  - PDF text extraction and chunking
  - Supabase ingestion
"""

import logging
from pathlib import Path

from app.core import UPLOADS_DIR, MAX_UPLOAD_SIZE_MB
from app.rag.uploader import ingest_pdf

logger = logging.getLogger(__name__)

# Constants
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024


async def upload_and_ingest_pdf(filename: str, contents: bytes) -> str:
    """
    Upload a PDF file and ingest it into the RAG knowledge base.
    
    Args:
        filename: Original filename (already sanitized).
        contents: Raw file bytes.
    
    Returns:
        Success message with chunk count.
    
    Raises:
        ValueError: If file is invalid.
        Exception: On ingestion failure.
    """
    # --- Validate file type ---
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are allowed")

    # --- Validate file size ---
    if len(contents) > MAX_UPLOAD_SIZE_BYTES:
        raise ValueError(
            f"File too large. Maximum allowed size is {MAX_UPLOAD_SIZE_MB} MB."
        )

    # --- Validate PDF magic bytes ---
    if not contents.startswith(b"%PDF"):
        raise ValueError("File is not a valid PDF")

    try:
        logger.info("Uploading file: %s (%d bytes)", filename, len(contents))

        # Save file to disk
        save_path = UPLOADS_DIR / filename
        save_path.write_bytes(contents)

        # Ingest into RAG system
        msg = ingest_pdf(str(save_path), filename)

        logger.info("File '%s' uploaded and ingested successfully", filename)
        return msg

    except Exception as exc:
        logger.error("Error uploading file: %s", exc, exc_info=True)
        raise
