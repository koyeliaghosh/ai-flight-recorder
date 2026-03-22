import mlflow
from src.agent import run_agent

def fetch_recent_runs(limit: int = 2):
    """
    Fetches past runs from the MLflow tracking server.
    Restricted exactly to `limit` (default 2) recent runs as requested.
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
        
    # Restrict strictly to top 2
    return df.head(limit).to_dict(orient="records")

def replay_run(run_id: str, new_prompt_version: str):
    """
    Reruns the agent using inputs from a previous trace.
    Returns the new trace ID and result.
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
        result = run_agent(query=original_query, prompt_version=new_prompt_version, max_tries=2)
        
    return {
        "new_run_id": new_run.info.run_id,
        "result": result
    }
