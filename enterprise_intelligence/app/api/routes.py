"""
API endpoint handlers for the Enterprise Intelligence system.

Implements health checks, query processing, and PDF uploads.
"""

import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.api.schemas import AskRequest, AskResponse, MessageResponse
from app.services.query_service import process_question
from app.services.pdf_service import upload_and_ingest_pdf

logger = logging.getLogger(__name__)

# Create a router for all endpoints
router = APIRouter()


# ─────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────
@router.get("/", response_model=MessageResponse, tags=["Health"])
async def root():
    """Health check — verify the API is running."""
    return MessageResponse(message="Enterprise Intelligence API is running")


# ─────────────────────────────────────────────────────────────
# Query Processing
# ─────────────────────────────────────────────────────────────
@router.post("/ask", response_model=AskResponse, tags=["Queries"])
async def ask(req: AskRequest):
    """
    Process a question through the agentic AI system.

    The question is routed to the most appropriate agent (RAG, web, stock, or PDF)
    and the result is returned.
    
    **Request:**
    - `question`: The user's question (max 5000 characters)
    
    **Response:**
    - `question`: Echo of the input question
    - `route`: Which agent handled the query (rag, web, stock, or pdf)
    - `answer`: The response from the agent
    """
    try:
        logger.info("Processing question: %s", req.question[:100])
        graph = get_graph()
        result = graph.invoke({"question": req.question})
        result = await process_question(req.question)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {exc}",
        )


# ─────────────────────────────────────────────────────────────
# PDF Upload & Ingestion
# ─────────────────────────────────────────────────────────────
@router.post("/upload-pdf", response_model=MessageResponse, tags=["Documents"])
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file for ingestion into the RAG knowledge base.

    The file is validated (type + size), saved to disk, then ingested
    page-by-page into the Supabase document store.
    
    **Validation:**
    - File must be PDF (checked by extension and magic bytes)
    - Maximum size: 50 MB (configurable)
    
    **Response:**
    - `message`: Success message with chunk count
    """
    # --- Validate file type ---
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # --- Validate content type ---
    if file.content_type and file.content_type != "application/pdf":
        raise HTTPExcepname ---
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # --- Validate content type ---
    if file.content_type and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a valid PDF")

    # --- Sanitise filename (prevent path traversal) ---
    safe_filename = Path(file.filename).name  # strips any directory components
    if not safe_filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # --- Read file contents ---
    contents = await file.read()

    try:
        msg = await upload_and_ingest_pdf(safe_filename, contents)
        return MessageResponse(message=msg)

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
