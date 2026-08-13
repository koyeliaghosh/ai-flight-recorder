import mlflow

@mlflow.trace(name="guardrail_check")
def check_financial_controls(query: str) -> bool:
    """
    Local Demo Guardrail
    If this were a production environment, this would call MLflow AI Gateway 3.12 guardrails.
    Returns True if safe, False if blocked.
    """
    forbidden_terms = ["refund", "ignore previous instructions", "bank account", "override", "bypass"]
    query_lower = query.lower()
    
    for term in forbidden_terms:
        if term in query_lower:
            mlflow.log_param("guardrail_status", "BLOCKED")
            mlflow.set_tag("guardrail.reason", f"Attempt to bypass financial reconciliation controls using term '{term}'.")
            return False
            
    mlflow.log_param("guardrail_status", "PASS")
    return True
