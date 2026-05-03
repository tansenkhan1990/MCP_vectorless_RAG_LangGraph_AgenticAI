from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY

client = create_client(SUPABASE_URL, SUPABASE_KEY)

def search_documents(query):

    result = client.table("private_company_details") \
        .select("*") \
        .text_search("content", query) \
        .limit(5) \
        .execute()

    rows = result.data

    if not rows:
        return "No company data found."

    return "\n\n".join([r["content"] for r in rows])