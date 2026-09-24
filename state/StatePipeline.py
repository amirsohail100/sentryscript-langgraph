from typing import Annotated, TypedDict


def merge_score_dicts(existing: dict, new_update: dict) -> dict:
    """Reducer: each parallel branch returns a partial dict; LangGraph merges
    them into one 'safety_scores' dict instead of overwriting it."""
    if existing is None:
        return new_update
    return {**existing, **new_update}


class AnalyzerState(TypedDict):
    raw_text: str
    safety_scores: Annotated[dict[str, int], merge_score_dicts]
