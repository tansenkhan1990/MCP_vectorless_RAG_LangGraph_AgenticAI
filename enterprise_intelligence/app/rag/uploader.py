import fitz
from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY

client = create_client(SUPABASE_URL, SUPABASE_KEY)

def chunk_text(text, size=1200):
    return [text[i:i+size] for i in range(0, len(text), size)]

def ingest_pdf(file_path, filename):

    doc = fitz.open(file_path)

    for page_num, page in enumerate(doc, start=1):

        text = page.get_text()

        chunks = chunk_text(text)

        for chunk in chunks:
            client.table("private_company_details").insert({
                "file_name": filename,
                "title": filename,
                "page_number": page_num,
                "content": chunk
            }).execute()

    return "PDF uploaded successfully"