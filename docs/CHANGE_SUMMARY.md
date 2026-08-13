# Change Summary

## Implemented Features
- **MLflow 3.12 Integration:** Fully pinned to 3.12.0. Native Trace UI embedded.
- **PromptOps:** Integrated MLflow Prompt Registry with aliases (`production`, `candidate`, `previous`).
- **Tracing Enhancements:** Tool spans and prompt metadata logged. Multimodal trace attachment feature added via `attachments.py`.
- **Evaluation Engine:** Deterministic scorers and an LLM Groundedness judge implemented, running on traces.
- **Replay Mechanism:** Allows selecting a trace and re-running the same inputs with the candidate prompt, presenting a side-by-side evaluation comparison.
- **Guardrails:** Added local financial control guardrail blocking prompt injection attempts.
- **Demo Mode:** Deterministic execution fallback mode (`DEMO_MODE=true`) for reliable meetup presentation without wifi.
- **UI Rewrite:** Streamlit application reorganized into 5 distinct tabs matching the PromptOps lifecycle.

## Remaining Limitations
- PDF generation is handled via `create_pdf.py` requiring `reportlab`. A dummy PDF needs to be manually created if `reportlab` fails to install on presentation machines.
- Evaluation currently uses deterministic checks in Demo Mode instead of calling an actual LLM judge to prevent API costs/latency during the live demo.
- Guardrails are a local fallback simulation of MLflow AI Gateway.
