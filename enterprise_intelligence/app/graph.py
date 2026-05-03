from langgraph.graph import StateGraph, END
from app.state import GraphState

from app.agents.router import router_node
from app.agents.rag_agent import rag_node
from app.agents.web_agent import web_node
from app.agents.stock_agent import stock_node
from app.agents.pdf_agent import pdf_node

builder = StateGraph(GraphState)

builder.add_node("router", router_node)
builder.add_node("rag", rag_node)
builder.add_node("web", web_node)
builder.add_node("stock", stock_node)
builder.add_node("pdf", pdf_node)

builder.set_entry_point("router")

builder.add_conditional_edges(
    "router",
    lambda x: x["route"],
    {
        "rag": "rag",
        "web": "web",
        "stock": "stock",
        "pdf": "pdf"
    }
)

builder.add_edge("rag", END)
builder.add_edge("web", END)
builder.add_edge("stock", END)
builder.add_edge("pdf", END)

graph = builder.compile()