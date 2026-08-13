import mlflow
from src.evaluation.deterministic import score_schema_validity, score_unsupported_claims, score_financial_control
from src.evaluation.judges import score_groundedness

def run_evaluation(response: str) -> dict:
    """
    Runs the evaluation suite on a response.
    """
    eval_results = {}
    
    # Deterministic
    eval_results["Schema Validity"] = score_schema_validity(response)
    eval_results["Unsupported Claims"] = score_unsupported_claims(response)
    eval_results["Financial Control"] = score_financial_control(response)
    
    # LLM Judge (or deterministic fallback)
    eval_results["Groundedness"] = score_groundedness(response)
    
    return eval_results

def mlf_evaluate_run(run_id: str):
    """
    Evaluates a specific MLflow run and logs the metrics back to it.
    """
    run = mlflow.get_run(run_id)
    response = run.data.tags.get("agent.final_response", "")
    
    results = run_evaluation(response)
    
    # Log scores back to MLflow trace/run
    with mlflow.start_run(run_id=run_id):
        for metric_name, result in results.items():
            safe_name = metric_name.replace(" ", "_").lower()
            mlflow.log_metric(f"eval_{safe_name}_score", result["score"])
            mlflow.set_tag(f"eval_{safe_name}_pass", str(result["pass"]))
            
    return results
