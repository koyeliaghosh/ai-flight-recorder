import os
import sys
import mlflow
from src.prompts.registry import init_registry, get_aliases, get_prompt_by_alias, promote_candidate, rollback_production
from src.agent import run_agent
from src.evaluator import mlf_evaluate_run
from src.replay import replay_run
from src.reset_demo import reset_demo

def run_smoke_test():
    print(f"Testing MLflow version... (Found: {mlflow.__version__})")
    assert mlflow.__version__ == "3.12.0", f"Expected MLflow 3.12.0 but got {mlflow.__version__}"
    
    # Initialize backend
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("Agent_Flight_Recorder")
    os.environ["DEMO_MODE"] = "true"
    
    print("Initializing Prompt Registry...")
    init_registry()
    aliases = get_aliases()
    assert "production" in aliases, "Production alias missing"
    assert "candidate" in aliases, "Candidate alias missing"
    
    print("Running Happy Path Scenario...")
    with mlflow.start_run(run_name="Smoke_Happy") as run:
        res = run_agent("Reconcile PO-999 against Invoice 1234", "production")
    happy_run_id = run.info.run_id
    assert res["response"], "No response from happy path"
    
    print("Running Hallucination Scenario...")
    with mlflow.start_run(run_name="Smoke_Hallucination") as run:
        res_hal = run_agent("Reconcile PO-888 against Invoice 5678", "production")
    hal_run_id = run.info.run_id
    
    print("Testing Evaluation...")
    eval_orig = mlf_evaluate_run(hal_run_id)
    assert "Groundedness" in eval_orig
    
    print("Testing Replay with Candidate...")
    replay_res = replay_run(hal_run_id, "candidate")
    assert "new_run_id" in replay_res
    
    print("Testing Prompt Promotion...")
    success = promote_candidate()
    assert success, "Promotion failed"
    
    print("Testing Prompt Rollback...")
    success = rollback_production()
    assert success, "Rollback failed"
    
    print("Resetting Demo...")
    reset_demo()
    
    print("Smoke test passed successfully!")

if __name__ == "__main__":
    run_smoke_test()
