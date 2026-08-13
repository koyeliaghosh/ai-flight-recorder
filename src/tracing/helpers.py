import mlflow

def log_agent_execution(query: str, prompt_version: str, prompt_alias: str, mode: str):
    """
    Logs standard metadata for the agent run.
    """
    mlflow.log_param("session_id", "demo-session")
    mlflow.log_param("scenario", "reconciliation")
    mlflow.log_param("environment", "demo")
    mlflow.log_param("demo_mode", mode)
    
    mlflow.log_param("prompt_name", "reconciliation-agent")
    mlflow.log_param("prompt_version", prompt_version)
    mlflow.log_param("prompt_alias", prompt_alias)
    mlflow.log_param("query", query)

def get_trace_id() -> str:
    """Helper to safely fetch the current active trace ID."""
    run = mlflow.active_run()
    if run:
        return run.info.run_id
    return ""
