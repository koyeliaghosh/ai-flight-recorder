import mlflow
from src.agent import run_agent
from src.evaluator import mlf_evaluate_run
from src.evaluation.compare import compare_evaluations

def fetch_recent_runs(limit: int = 5):
    """
    Fetches past runs from the MLflow tracking server.
    """
    experiment = mlflow.get_experiment_by_name("Agent_Flight_Recorder")
    if not experiment or not experiment.experiment_id:
        return []
        
    df = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        max_results=limit,
        order_by=["start_time DESC"]
    )
    if df.empty:
        return []
    
    if "params.query" not in df.columns:
        return []
        
    # Filter to runs that actually have a query param
    df = df[df["params.query"].notnull()]
    if df.empty:
        return []
        
    return df.head(limit).to_dict(orient="records")

def replay_run(run_id: str, new_prompt_alias: str):
    """
    Reruns the agent using inputs from a previous trace and a candidate prompt alias.
    Returns the new trace ID, result, and evaluation comparison.
    """
    # Fetch old run inputs from MLflow
    run = mlflow.get_run(run_id)
    original_query = run.data.params.get("query", "")
    if not original_query:
        return {"error": "Run had no tracking query logged."}
    
    # Rerun agent
    with mlflow.start_run(run_name=f"Replay_of_{run_id}") as new_run:
        mlflow.log_param("is_replay", True)
        mlflow.log_param("original_run_id", run_id)
        result = run_agent(query=original_query, prompt_alias=new_prompt_alias, max_tries=2)
        
    new_run_id = new_run.info.run_id
    
    # Evaluate both
    eval_orig = mlf_evaluate_run(run_id)
    eval_new = mlf_evaluate_run(new_run_id)
    
    comparison = compare_evaluations(eval_orig, eval_new)
    
    return {
        "new_run_id": new_run_id,
        "result": result,
        "comparison": comparison
    }
