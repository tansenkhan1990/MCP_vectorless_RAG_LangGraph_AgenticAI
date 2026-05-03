from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY

client = create_client(SUPABASE_URL, SUPABASE_KEY)

def search_documents(query):
    result = client.rpc(
        "search_private_company_details",
        {
            "search_query": query,
            "match_count": 5
        }
    ).execute()

    rows = result.data

    if not rows:
        return "No company data found."

    return "\n\n".join([r["chunk_text"] for r in rows])