import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from state.StatePipeline import AnalyzerState

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", api_key=os.getenv("GROQ_API_KEY"))


def _score_prompt(instruction: str, raw_text: str) -> str:
    return (
        f"{instruction} Provide a score from 0 to 100. "
        "Return ONLY the plain integer number, nothing else.\n\n"
        f"Text:\n{raw_text}"
    )


def _safe_int(text: str) -> int:
    """Clamp to 0-100 and fall back to 0 if the model doesn't return a clean integer."""
    try:
        return max(0, min(100, int(text.strip())))
    except ValueError:
        return 0


def toxicity_node(state: AnalyzerState) -> dict:
    print("\n🤬 [Branch 1] Analyzing Toxicity and Hate Speech ...")
    prompt = _score_prompt(
        "Analyze the following text for profanity, aggression, hate speech, or toxicity, "
        "where 0 means perfectly clean and 100 means highly toxic.",
        state["raw_text"],
    )
    score = _safe_int(llm.invoke(prompt).content)
    return {"safety_scores": {"toxicity_level": score}}


def copyright_node(state: AnalyzerState) -> dict:
    print("\n©️ [Branch 2] Analyzing Copyright & Originality Risks ...")
    prompt = _score_prompt(
        "Judge if the following text sounds heavily plagiarized, unoriginal, or presents a "
        "corporate trademark risk, where 0 means entirely original and 100 means high risk.",
        state["raw_text"],
    )
    score = _safe_int(llm.invoke(prompt).content)
    return {"safety_scores": {"copyright_risk": score}}


def culture_node(state: AnalyzerState) -> dict:
    print("\n🌍 [Branch 3] Analyzing Regional & Cultural Sensitivity ...")
    prompt = _score_prompt(
        "Analyze the following text for regional sensitivities, political landmines, or "
        "cultural insensitivity that might offend a global audience, where 0 means completely "
        "safe and 100 means highly offensive.",
        state["raw_text"],
    )
    score = _safe_int(llm.invoke(prompt).content)
    return {"safety_scores": {"culture_insensitivity": score}}
