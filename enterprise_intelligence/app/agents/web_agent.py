from duckduckgo_search import DDGS

def web_node(state):

    with DDGS() as ddgs:
        results = list(ddgs.text(state["question"], max_results=5))

    text = "\n".join(
        [r["title"] + " - " + r["body"] for r in results]
    )

    return {"answer": text}