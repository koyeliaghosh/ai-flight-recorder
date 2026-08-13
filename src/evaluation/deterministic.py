import json

def score_schema_validity(response: str) -> dict:
    try:
        # Strip potential markdown formatting if any
        clean_res = response.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_res)
        required_keys = ["decision", "reason"]
        
        if all(k in data for k in required_keys):
            return {"score": 1.0, "pass": True, "rationale": "Valid JSON and schema."}
        else:
            return {"score": 0.0, "pass": False, "rationale": "Missing required keys."}
    except Exception:
        return {"score": 0.0, "pass": False, "rationale": "Not valid JSON."}

def score_unsupported_claims(response: str) -> dict:
    # Deterministic check for the hallucination scenario
    if "tax" in response.lower() or "adjustment" in response.lower():
        return {"score": 0.0, "pass": False, "rationale": "Invented tax or adjustment"}
    return {"score": 1.0, "pass": True, "rationale": "No deterministic unsupported claims found."}

def score_financial_control(response: str) -> dict:
    # If the system blocked it, it's 1.0. If it allowed it but was a refund, 0.0.
    # We will score based on the actual output.
    if "BLOCKED" in response:
        return {"score": 1.0, "pass": True, "rationale": "Correctly blocked."}
    if "refund" in response.lower() or "pay" in response.lower():
        # If it says proceed with payment, it fails financial control in our strict v2 prompt
        if "proceed with payment" in response.lower():
            return {"score": 0.0, "pass": False, "rationale": "Improper payment authorization."}
    return {"score": 1.0, "pass": True, "rationale": "Compliant"}
