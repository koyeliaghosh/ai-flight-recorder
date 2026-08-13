# Implementation Plan: AI Flight Recorder MLflow 3.12 Upgrade

## Goal Description
Enhance the existing AI Flight Recorder repository into a meetup-ready demonstration for MLflow 3.12, showcasing PromptOps, Observability, and AI Evaluation. The core use case (Financial Reconciliation) must be preserved, and the demo must reliably execute locally without external LLM dependencies (Demo Mode).

## Open Questions
- Is there any specific local model provider preference for non-demo live mode, or should we just maintain the existing Vertex AI integration and rely primarily on Demo Mode for the meetup?
- Should the mock PDF for Invoice 5678 be generated programmatically during demo setup, or is a static pre-generated PDF sufficient?

## Proposed Changes

### Phase 1 — MLflow 3.12 Compatibility
- **Summary:** Pin MLflow version and remove incorrect version claims.
- **Files:**
  - `requirements.txt`: Update MLflow to `3.12.0`.
  - `README.md`, `Dockerfile`, `app.py`: Remove references to 3.13 or 3.10 and enforce 3.12.0 branding.

### Phase 2 — Prompt Registry
- **Summary:** Create a setup script to populate the MLflow Prompt Registry with `reconciliation-agent` prompt (v1 baseline, v2 governed) and their aliases.
- **Files:**
  - `src/prompts/registry.py` [NEW]: Logic to create/fetch prompts and manage aliases (`production`, `candidate`, `previous`).
  - `src/prompts/baseline.txt` [NEW]: V1 prompt template.
  - `src/prompts/governed.txt` [NEW]: V2 governed prompt template.
  - `src/agent.py`: Modify `run_agent` to fetch the prompt via its alias from the registry instead of hardcoding.

### Phase 3 — Flight Recorder Tracing
- **Summary:** Enhance tracing spans, add prompt lineage, and attach a multimodal PDF.
- **Files:**
  - `src/tracing/helpers.py` [NEW]: Utilities for structured span logging.
  - `src/tracing/attachments.py` [NEW]: Logic to attach `invoice_5678.pdf` to the trace.
  - `data/invoice_5678.pdf` [NEW]: Mock PDF for the demo.
  - `src/agent.py`: Update trace attributes, log prompt aliases/versions, log latency/tokens, and attach the PDF.

### Phase 4 — Evaluation
- **Summary:** Implement deterministic scorers and a groundedness judge, running against a test dataset.
- **Files:**
  - `src/evaluation/dataset.py` [NEW]: 12 reconciliation evaluation cases.
  - `src/evaluation/deterministic.py` [NEW]: Deterministic scorers (correctness, schema validity, financial control).
  - `src/evaluation/judges.py` [NEW]: Groundedness LLM judge (or deterministic fallback in Demo Mode).
  - `src/evaluation/compare.py` [NEW]: Aggregation of metrics for Production vs Candidate.
  - `src/evaluator.py`: Refactor to execute the scorers on the trace payload.

### Phase 5 — Replay
- **Summary:** Rework replay to rerun the scenario using the `candidate` prompt, and compare evaluations.
- **Files:**
  - `src/replay.py`: Update to pull inputs from the original trace and execute with the `candidate` alias. Format comparison output.

### Phase 6 — PromptOps
- **Summary:** Provide alias promotion and rollback mechanisms.
- **Files:**
  - `src/prompts/registry.py`: Add `promote_candidate()` and `rollback_production()` functions.

### Phase 7 — Guardrails
- **Summary:** Implement a local fallback guardrail to intercept adversarial prompts.
- **Files:**
  - `src/guardrails/financial_controls.py` [NEW]: Guardrail logic to block unauthorized refunds/modifications.
  - `src/agent.py`: Integrate guardrail check before execution.

### Phase 8 — UI
- **Summary:** Refactor Streamlit to a 5-tab design.
- **Files:**
  - `app.py`: Reorganize into Run Agent, Flight Recorder, Evaluate, Replay & Improve, PromptOps tabs. Integrate backend functions for evaluation comparisons and PromptOps operations.

### Phase 9 — Reliability
- **Summary:** Formalize Demo Mode and provide smoke/reset scripts.
- **Files:**
  - `src/config.py` [NEW]: Define `DEMO_MODE=true` environment parsing.
  - `src/smoke_test.py` [NEW]: Comprehensive automated smoke test.
  - `src/reset_demo.py` [NEW]: Script to restore prompt aliases for the meetup demo.
  - `tests/` [NEW]: Unit tests for various components.

### Phase 10 — Documentation
- **Summary:** Update README and provide presenter scripts.
- **Files:**
  - `README.md`: Document new features and 3.12 highlights.
  - `docs/DEMO_SCRIPT.md` [NEW]: 15-20 minute walkthrough script.
  - `docs/CHANGE_SUMMARY.md` [NEW]: Final deliverables summary.

## Verification Plan

### Automated Tests
- Run `pytest` on the new `tests/` directory to verify tools, deterministic evaluation, and guardrails.
- Run `python -m src.smoke_test` to verify end-to-end integration, prompt promotion, and replay functionality.

### Manual Verification
- Start the Streamlit app (`streamlit run app.py`) with `DEMO_MODE=true`.
- Execute the Happy Path and Adversarial Attack scenarios in the UI.
- Verify traces and PDF attachments in the MLflow UI (`sqlite:///mlflow.db`).
- Execute evaluation, run replay, and promote the candidate in the respective tabs.
