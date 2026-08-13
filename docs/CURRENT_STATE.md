# Current State of AI Flight Recorder

## Architecture and Stack
- **Framework:** Streamlit for the UI (`app.py`), running a multi-tab interface.
- **Tracing:** MLflow is used for tracking and tracing. The current version in `requirements.txt` is `3.13.0`.
- **LLM Provider:** Vertex AI with `gemini-1.0-pro` is configured, but there is a robust fallback mechanism to a deterministic "mock agent" when credentials or internet are unavailable (`src/agent.py`).
- **Use Case:** Financial Reconciliation Agent matching Invoices, Purchase Orders (POs), and Suppliers.

## Functionality
- **Data Source:** Hardcoded sample data in `src/sample_data.py`.
- **Retrieval:** Three tools exist in `src/retrieval.py` for fetching invoices, POs, and suppliers.
- **Agent Logic:** `src/agent.py` implements a run_agent function with tracing (`@mlflow.trace`) and manual span tracking (`mlflow.start_span`). It simulates a conversation loop and executes tools until a decision is reached or `max_tries` is hit.
- **UI Tabs:**
  - **Guided Scenarios:** Runs 4 predefined scenarios (Happy Path, Logic Discrepancy, Adversarial Attack, Tool Error).
  - **Trace Dashboard:** Embedded MLflow UI (`<iframe>`).
  - **Replay & Fix:** Fetches recent runs and allows replaying with a different prompt string (e.g., "v1" or "v2-adversarial").
- **Prompts:** Hard-coded as strings/versions passed around. There is no MLflow Prompt Registry integration.
- **Evaluation:** `src/evaluator.py` contains a stub `mlf_evaluate_run` that blindly logs static metrics (`relevance_score`, `completeness_score`, `hallucination_risk`) to MLflow. There is no real deterministic or LLM-based evaluation of the payload.
- **Guardrails:** No AI Gateway or structured local guardrails; just a mock response hardcoded in `src/agent.py` to block "12345" or "Ignore".

## Missing MLflow 3.12 Requirements
- **MLflow Version:** Currently 3.13.0; needs to be pinned to 3.12.0.
- **Prompt Registry:** Not used.
- **Prompt Aliases:** Not used (production, candidate, previous).
- **Prompt-to-Trace Lineage:** Trace doesn't properly link an MLflow Prompt Registry prompt.
- **Multimodal Tracing (PDF):** No PDF attachment feature implemented.
- **Structured Response:** No Pydantic schema validation.
- **Evaluation:** No deterministic evaluation logic or real Groundedness judge implementation. Evaluation comparison UI is absent.
- **PromptOps UI:** No UI tab for promoting or rolling back prompt aliases.
