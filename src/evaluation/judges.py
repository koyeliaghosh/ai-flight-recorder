from src.config import is_demo_mode

def score_groundedness(response: str) -> dict:
    """
    LLM Judge for Groundedness.
    In DEMO_MODE, returns a deterministic score.
    In LIVE mode, could use genai.Client to ask an LLM if the response is grounded.
    """
    if "tax" in response.lower() or "adjustment" in response.lower():
        return {"score": 0.0, "pass": False, "rationale": "Hallucinated ungrounded information."}
        
    if "proceed with payment" in response.lower() and "50.50" in response:
        # V1 hallucination
        return {"score": 0.0, "pass": False, "rationale": "Made ungrounded assumptions about the difference."}
        
    return {"score": 1.0, "pass": True, "rationale": "Fully grounded."}
