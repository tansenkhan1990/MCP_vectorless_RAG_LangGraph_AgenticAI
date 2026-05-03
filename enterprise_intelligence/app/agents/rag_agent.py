from app.rag.retriever import search_documents

def rag_node(state):
    return {"answer": search_documents(state["question"])}