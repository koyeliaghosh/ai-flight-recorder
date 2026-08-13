import os

def is_demo_mode() -> bool:
    """
    Returns True if DEMO_MODE is true. 
    Defaults to False if not set (meaning real Vertex AI execution by default).
    """
    return os.environ.get("DEMO_MODE", "false").lower() == "true"
