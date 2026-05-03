from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import shutil

from app.graph import graph
from app.rag.uploader import ingest_pdf

app = FastAPI()

class AskRequest(BaseModel):
    question: str

@app.post("/ask")
def ask(req: AskRequest):
    return graph.invoke({"question": req.question})

@app.post("/upload-pdf")
def upload_pdf(file: UploadFile = File(...)):

    path = f"uploads/{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    msg = ingest_pdf(path, file.filename)

    return {"message": msg}