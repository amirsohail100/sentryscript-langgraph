from langgraph.graph import StateGraph, START, END

from state.AnalyzerState import AnalyzerState
from tools.nodes import toxicity_node, copyright_node, culture_node

builder = StateGraph(AnalyzerState)

builder.add_node("toxicity", toxicity_node)
builder.add_node("copyright", copyright_node)
builder.add_node("culture", culture_node)

# START se teeno branches parallel me fire hoti hain, aur teeno independently END tak jaati hain.
# safety_scores state ka merge_score_dicts reducer teeno ke partial dict outputs ko
# ek hi dict me combine kar deta hai.
builder.add_edge(START, "toxicity")
builder.add_edge(START, "copyright")
builder.add_edge(START, "culture")

builder.add_edge("toxicity", END)
builder.add_edge("copyright", END)
builder.add_edge("culture", END)

compiled_graph = builder.compile()


def run_analysis(raw_text: str) -> dict:
    """Fans raw_text out to 3 independent safety checks and returns the merged scores."""
    result = compiled_graph.invoke({"raw_text": raw_text, "safety_scores": {}})
    return result["safety_scores"]
