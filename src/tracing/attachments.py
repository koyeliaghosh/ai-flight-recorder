import os
import mlflow

def attach_pdf_to_trace(pdf_path: str):
    """
    Attaches a PDF to the current active MLflow run/trace.
    """
    if os.path.exists(pdf_path):
        mlflow.log_artifact(pdf_path, artifact_path="attachments")
    else:
        print(f"Warning: Could not find attachment PDF at {pdf_path}")
