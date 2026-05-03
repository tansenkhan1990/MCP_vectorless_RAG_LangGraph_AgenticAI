import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, validator
import shutil

from app.graph import graph
from app.rag.uploader import ingest_pdf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Enterprise Intelligence API", version="1.0.0")

class AskRequest(BaseModel):
    question: str
    
    @validator('question')
    def question_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty')
        return v

@app.post("/ask")
async def ask(req: AskRequest):
    """
    Process a question through the agentic AI system.
    
    Args:
        req (AskRequest): The request containing the question
        
    Returns:
        dict: The response from the agentic AI system
    """
    try:
        logger.info(f"Processing question: {req.question}")
        result = graph.invoke({"question": req.question})
        logger.info("Question processed successfully")
        return result
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file for ingestion into the RAG system.
    
    Args:
        file (UploadFile): The PDF file to upload
        
    Returns:
        dict: Success message
    """
    try:
        logger.info(f"Uploading file: {file.filename}")
        
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        path = f"uploads/{file.filename}"
        
        # Save file
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Ingest PDF
        msg = ingest_pdf(path, file.filename)
        
        logger.info(f"File {file.filename} uploaded and ingested successfully")
        return {"message": msg}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running.
    
    Returns:
        dict: Welcome message
    """
    return {"message": "Enterprise Intelligence API is running"}