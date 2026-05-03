def router_node(state):

    q = state["question"].lower()

    if "pdf" in q or "report" in q:
        return {"route": "pdf"}

    if "stock" in q or "tesla" in q or "apple" in q:
        return {"route": "stock"}

    if "news" in q or "politics" in q or "latest":
        return {"route": "web"}

    return {"route": "rag"}