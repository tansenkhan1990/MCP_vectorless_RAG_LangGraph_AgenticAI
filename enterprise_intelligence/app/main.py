"""
Enterprise Intelligence API — FastAPI application entry point.

Endpoints:
    GET  /          Health check
    POST /ask       Process a question through the agentic AI system
    POST /upload-pdf   Upload and ingest a PDF into the RAG knowledge base
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from collections import defaultdict

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from app.config import UPLOADS_DIR, validate_config, MAX_UPLOAD_SIZE_MB
from app.graph import get_graph
from app.rag.uploader import ingest_pdf

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Rate limiting (simple in-memory implementation)
RATE_LIMIT_REQUESTS = 10  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds
_request_log: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(client_ip: str) -> tuple[bool, int]:
    """
    Check if client has exceeded rate limit.
    
    Returns:
        (is_allowed, remaining_requests)
    """
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    
    # Clean old requests
    _request_log[client_ip] = [t for t in _request_log[client_ip] if t > window_start]
    
    # Check limit
    if len(_request_log[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False, 0
    
    _request_log[client_ip].append(now)
    remaining = RATE_LIMIT_REQUESTS - len(_request_log[client_ip])
    return True, remaining


# ---------------------------------------------------------------------------
# Lifespan — run startup / shutdown logic
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup and shutdown events."""
    # Startup
    try:
        warnings = validate_config()
        if warnings:
            logger.warning("Config warnings: %s", warnings)
    except ValueError as exc:
        logger.error("Configuration error: %s", exc)
        raise

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Uploads directory ready: %s", UPLOADS_DIR)
    logger.info("Enterprise Intelligence API started")

    yield  # ← app is running

    # Shutdown
    logger.info("Enterprise Intelligence API shutting down")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Enterprise Intelligence API",
    description="Agentic AI system with RAG, web search, stock data, and PDF generation.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins in dev; tighten for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Apply rate limiting to all requests.
    
    Limits expensive operations (/ask, /upload-pdf) per IP.
    """
    # Only rate limit expensive operations
    if request.url.path in ["/ask", "/upload-pdf"]:
        client_ip = request.client.host if request.client else "unknown"
        is_allowed, remaining = _check_rate_limit(client_ip)
        
        if not is_allowed:
            logger.warning("Rate limit exceeded for client: %s", client_ip)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds."
                }
            )
    
    return await call_next(request)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class AskRequest(BaseModel):
    """Request body for the /ask endpoint."""
    question: str

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Question cannot be empty")
        if len(v) > 5000:
            raise ValueError("Question cannot exceed 5000 characters")
        return v.strip()


class AskResponse(BaseModel):
    """Response body for the /ask endpoint."""
    question: str
    route: str | None = None
    answer: str | None = None


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/", response_model=MessageResponse)
async def root():
    """Health check — verify the API is running."""
    return MessageResponse(message="Enterprise Intelligence API is running")


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    """
    Process a question through the agentic AI system.

    The question is routed to the most appropriate agent (RAG, web, stock, or PDF)
    and the result is returned.
    """
    try:
        logger.info("Processing question: %s", req.question[:100])
        graph = get_graph()
        result = graph.invoke({"question": req.question})
        logger.info("Question processed — route=%s", result.get("route"))
        return AskResponse(**result)
    except Exception as exc:
        logger.error("Error processing question: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {exc}",
        )


@app.post("/upload-pdf", response_model=MessageResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file for ingestion into the RAG knowledge base.

    The file is validated (type + size), saved to disk, then ingested
    page-by-page into the Supabase document store.
    """
    # --- Validate file type ---
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # --- Validate content type ---
    if file.content_type and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a valid PDF")

    # --- Sanitise filename (prevent path traversal) ---
    safe_filename = Path(file.filename).name  # strips any directory components
    if not safe_filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # --- Validate file size ---
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {MAX_UPLOAD_SIZE_MB} MB.",
        )

    # --- Validate PDF magic bytes ---
    if not contents.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="File is not a valid PDF")

    try:
        logger.info("Uploading file: %s (%d bytes)", safe_filename, len(contents))

        save_path = UPLOADS_DIR / safe_filename
        save_path.write_bytes(contents)

        msg = ingest_pdf(str(save_path), safe_filename)

        logger.info("File '%s' uploaded and ingested successfully", safe_filename)
        return MessageResponse(message=msg)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error uploading file: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {exc}",
        )