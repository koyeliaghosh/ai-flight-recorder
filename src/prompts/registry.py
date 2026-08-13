import os
import mlflow
from mlflow import MlflowClient

PROMPT_NAME = "reconciliation-agent"

def _read_prompt(filename: str) -> str:
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def init_registry():
    """
    Initializes the MLflow Prompt Registry with v1 (baseline) and v2 (governed) prompts
    and sets up their initial aliases.
    """
    client = MlflowClient()
    
    # Create registered model if it doesn't exist
    try:
        client.create_registered_model(name=PROMPT_NAME, description="Financial Reconciliation Agent Prompt")
    except Exception:
        pass # Already exists
        
    # Check if versions already exist to avoid creating duplicates on every run
    versions = client.search_model_versions(f"name='{PROMPT_NAME}'")
    if len(versions) >= 2:
        return # Registry already populated
        
    baseline_template = _read_prompt("baseline.txt")
    governed_template = _read_prompt("governed.txt")
    
    # We must mock creating a prompt since natively in MLflow 3.12, prompts are just models
    # where the payload is logged as a langchain/pyfunc model, but MLflow 3.12 added the prompt registry
    # using `mlflow.models.set_model`. Wait, MLflow 3.12 has `mlflow.log_dict` or `mlflow.langchain.log_model`.
    # Let's log them simply as strings in a run and register them as model versions.
    # But MLflow 3.12 might have `mlflow.prompts` or similar. Let's just create model versions 
    # directly using runs, or assume we will store prompt templates as artifacts.
    # A lightweight way for the demo is to log the prompt text as an artifact, then register it.
    
    def log_and_register_prompt(template, version_msg):
        with mlflow.start_run(run_name=f"register_{version_msg}"):
            with open("prompt.txt", "w") as f:
                f.write(template)
            mlflow.log_artifact("prompt.txt")
            run_id = mlflow.active_run().info.run_id
            
        mv = client.create_model_version(
            name=PROMPT_NAME,
            source=f"runs:/{run_id}/prompt.txt",
            run_id=run_id,
            description=version_msg
        )
        return mv.version
        
    v1_ver = log_and_register_prompt(baseline_template, "Initial baseline reconciliation prompt")
    v2_ver = log_and_register_prompt(governed_template, "Add grounding, structured output, financial controls and abstention")
    
    client.set_registered_model_alias(PROMPT_NAME, "baseline", v1_ver)
    client.set_registered_model_alias(PROMPT_NAME, "previous", v1_ver)
    client.set_registered_model_alias(PROMPT_NAME, "production", v1_ver)
    client.set_registered_model_alias(PROMPT_NAME, "candidate", v2_ver)


def get_prompt_by_alias(alias: str) -> tuple[str, str]:
    """
    Returns (prompt_template_string, version_number) for the given alias.
    """
    client = MlflowClient()
    try:
        mv = client.get_model_version_by_alias(PROMPT_NAME, alias)
        # Download the artifact
        local_path = client.download_artifacts(mv.run_id, "prompt.txt")
        with open(local_path, "r", encoding="utf-8") as f:
            template = f.read()
        return template, mv.version
    except Exception as e:
        print(f"Error fetching prompt by alias {alias}: {e}")
        return "", ""

def promote_candidate():
    """
    Promote candidate to production.
    Before: production -> v1, candidate -> v2
    After: previous -> v1, production -> v2
    """
    client = MlflowClient()
    try:
        prod_mv = client.get_model_version_by_alias(PROMPT_NAME, "production")
        cand_mv = client.get_model_version_by_alias(PROMPT_NAME, "candidate")
        
        client.set_registered_model_alias(PROMPT_NAME, "previous", prod_mv.version)
        client.set_registered_model_alias(PROMPT_NAME, "production", cand_mv.version)
        return True
    except Exception as e:
        print(f"Promotion failed: {e}")
        return False

def rollback_production():
    """
    Rollback production to previous.
    """
    client = MlflowClient()
    try:
        prev_mv = client.get_model_version_by_alias(PROMPT_NAME, "previous")
        client.set_registered_model_alias(PROMPT_NAME, "production", prev_mv.version)
        return True
    except Exception as e:
        print(f"Rollback failed: {e}")
        return False

def get_aliases() -> dict:
    """Returns current mapping of alias to version number."""
    client = MlflowClient()
    try:
        model = client.get_registered_model(PROMPT_NAME)
        return {alias: mv for alias, mv in model.aliases.items()}
    except Exception:
        return {}
