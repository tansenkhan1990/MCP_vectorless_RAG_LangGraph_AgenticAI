from typing import TypedDict, Optional

class GraphState(TypedDict):
    question: str
    route: Optional[str]
    answer: Optional[str]