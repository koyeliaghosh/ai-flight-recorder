# Live Meetup Demo Script (15-20 min)

1. **Introduction & Context (2 min)**
   - Explain the "AI Flight Recorder" concept: tracing what happened, evaluating it, and safely improving it.
   - Show the Streamlit UI (Tab 1: Run Agent).

2. **Run Failure (3 min)**
   - Execute the "Reconciliation Hallucination" scenario.
   - Point out that the agent (v1 baseline) hallucinated a tax/adjustment justification to reconcile the $50.50 difference.

3. **Inspect Trace & PDF (3 min)**
   - Switch to Tab 2: Flight Recorder.
   - Open the MLflow 3.12 trace.
   - Show the Trace Graph View, pointing out tool spans and the LLM span.
   - Open the attached `invoice_5678.pdf` directly from the trace to prove the agent's hallucination using multimodal observability.

4. **Evaluate (2 min)**
   - Switch to Tab 3: Evaluate.
   - Run evaluation on the failed trace.
   - Show that Groundedness and Unsupported Claims scorers both report failures (0.0 score).

5. **Replay & Compare (3 min)**
   - Switch to Tab 4: Replay & Improve.
   - Select the failed run and click "Replay with Candidate".
   - Show the side-by-side comparison: Candidate v2 correctly abstains and flags the discrepancy without inventing a reason.
   - Note the improved evaluation scores for the Candidate run.

6. **Promote Candidate (2 min)**
   - Switch to Tab 5: PromptOps.
   - Show the two prompt versions and their aliases.
   - Click "Promote Candidate to Production".

7. **Guardrail Demonstration (2 min)**
   - Go back to Tab 1: Run Agent.
   - Run the "Financial Control Attack" scenario.
   - Show how the Guardrail intercepts the prompt injection before LLM execution, returning "BLOCKED".

8. **Close (1 min)**
   - Summarize the PromptOps lifecycle demonstrated.
