import mlflow
from src.prompts.registry import init_registry, get_aliases, PROMPT_NAME
from mlflow import MlflowClient

def reset_demo():
    print("Resetting demo to initial state...")
    init_registry()
    
    client = MlflowClient()
    aliases = get_aliases()
    
    if "candidate" in aliases:
        cand_ver = aliases["candidate"]
    else:
        print("Candidate version not found, initializing registry might have failed.")
        return
        
    # We assume v1 is version 1 and v2 is version 2, but we can just use the known structure
    # Let's find version 1 and version 2 based on description or just assume lowest is v1
    model = client.get_registered_model(PROMPT_NAME)
    versions = client.search_model_versions(f"name='{PROMPT_NAME}'")
    versions = sorted(versions, key=lambda x: int(x.version))
    
    if len(versions) >= 2:
        v1_ver = versions[0].version
        v2_ver = versions[1].version
        
        client.set_registered_model_alias(PROMPT_NAME, "production", v1_ver)
        client.set_registered_model_alias(PROMPT_NAME, "previous", v1_ver)
        client.set_registered_model_alias(PROMPT_NAME, "candidate", v2_ver)
        print("Demo restored: production -> v1, candidate -> v2, previous -> v1.")
    else:
        print("Not enough versions to reset.")

if __name__ == "__main__":
    reset_demo()
