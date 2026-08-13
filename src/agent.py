import os
import json
import time
import mlflow
from typing import Optional

from google import genai
from google.genai import types

from src.retrieval import get_invoice_details, get_purchase_order_details, get_supplier_info
from src.prompts.registry import get_prompt_by_alias
from src.config import is_demo_mode
from src.tracing.helpers import log_agent_execution
from src.tracing.attachments import attach_pdf_to_trace
from src.guardrails.financial_controls import check_financial_controls

# Attempt to configure GenAI client if not in Demo Mode
client = None
if not is_demo_mode():
    try:
        # Client initialized using default ADC credentials
        project = os.environ.get("GOOGLE_CLOUD_PROJECT", "ai-flight-recorder")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
        client = genai.Client(vertexai=True, project=project, location=location)
    except Exception as e:
        print(f"Warning: Failed to initialize google-genai client. Error: {e}")

# Tool wrapper list for GenAI
# Python functions directly serve as tools in google-genai
tools_list = [get_invoice_details, get_purchase_order_details, get_supplier_info]

FUNC_MAP = {
    "get_invoice_details": get_invoice_details,
    "get_purchase_order_details": get_purchase_order_details,
    "get_supplier_info": get_supplier_info
}

@mlflow.trace(name="run_reconciliation_agent")
def run_agent(query: str, prompt_alias: str = "production", max_tries: int = 2) -> dict:
    """
    Core agent execution function with strict max_tries limit.
    Traced heavily by MLflow.
    """
    mode_str = "demo (offline)" if is_demo_mode() or client is None else "live (vertex)"
    
    # Fetch prompt from registry
    system_prompt, version_num = get_prompt_by_alias(prompt_alias)
    if not system_prompt:
        # Fallback if registry not initialized
        system_prompt = f"You are an AI Invoice Reconciliation Agent. Prompt alias: {prompt_alias}"
        version_num = "unknown"
        
    log_agent_execution(query, version_num, prompt_alias, mode_str)
    mlflow.log_param("max_tries", max_tries)
    
    # 1. Guardrail Check
    if not check_financial_controls(query):
        res = "BLOCKED\n\nReason:\nAttempt to bypass financial reconciliation controls."
        mlflow.set_tag("agent.final_response", res)
        return {"response": res, "tries": 0}
        
    # 2. Attach PDF if relevant to trace
    if "5678" in query:
        invoice_path = os.path.join("data", "invoice_5678.pdf")
        po_path = os.path.join("data", "po_888.pdf")
        attach_pdf_to_trace(invoice_path)
        attach_pdf_to_trace(po_path)

    # 3. Fallback deterministic execution for DEMO_MODE
    if is_demo_mode() or client is None:
        return run_deterministic_demo(query, prompt_alias, max_tries)

    # 4. Live Execution via Vertex AI
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    mlflow.log_param("model_provider", "vertex_ai")
    mlflow.log_param("model_name", model_name)
    
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=tools_list,
        temperature=0.0
    )
    
    chat = client.chats.create(model=model_name, config=config)
    
    current_try = 0
    final_response = ""
    message = query
    start_time = time.time()
    
    while current_try < max_tries:
        current_try += 1
        try:
            with mlflow.start_span(name="llm_call") as span:
                response = chat.send_message(message)
                span.set_attribute("candidates_count", len(response.candidates) if response.candidates else 0)
                
                # Check if it was a function call
                if response.function_calls:
                    tool_responses = []
                    with mlflow.start_span(name="execute_tools") as tspan:
                        for fn_call in response.function_calls:
                            func_name = fn_call.name
                            args = fn_call.args
                            if func_name in FUNC_MAP:
                                result = FUNC_MAP[func_name](**args)
                                tool_responses.append(
                                    types.Part.from_function_response(
                                        name=func_name,
                                        response={"result": result}
                                    )
                                )
                            else:
                                tool_responses.append(
                                    types.Part.from_function_response(
                                        name=func_name,
                                        response={"error": "Tool not found"}
                                    )
                                )
                    message = tool_responses
                else:
                    final_response = response.text or ""
                    break
        except Exception as e:
            with mlflow.start_span(name="vertex_api_error") as span:
                span.set_attribute("error", str(e))
                mlflow.set_tag("agent.error", str(e))
                mlflow.log_param("failure_category", "API_ERROR")
            final_response = f"Agent Error: {str(e)}"
            break
            
    latency = time.time() - start_time
    mlflow.log_metric("latency", latency)
    
    if current_try >= max_tries and not final_response:
        final_response = "Agent aborted: Reached strict max_tries limit of 2."
        mlflow.log_param("failure_category", "MAX_TRIES_EXCEEDED")
        
    mlflow.log_metric("tool_call_count", current_try - 1 if final_response else current_try)
    mlflow.set_tag("agent.final_response", final_response)
    
    return {
        "response": final_response,
        "tries": current_try
    }


def run_deterministic_demo(query: str, prompt_alias: str, max_tries: int) -> dict:
    """Deterministic fallback for DEMO_MODE"""
    mlflow.log_param("model_provider", "deterministic_demo")
    mlflow.log_param("model_name", "mock")
    start_time = time.time()
    
    # Execute tools statically to capture spans
    with mlflow.start_span(name="llm_call"):
        pass
    
    with mlflow.start_span(name="execute_tools"):
        if "888" in query and "5678" in query:
            get_invoice_details("5678")
            get_purchase_order_details("PO-888")
        elif "999" in query and "1234" in query:
            get_invoice_details("1234")
            get_purchase_order_details("PO-999")
        elif "9999" in query or "ERROR" in query:
            get_purchase_order_details("PO-ERROR-999")
            
    # Determine behavior based on prompt alias
    is_v2 = (prompt_alias == "candidate") or ("v2" in prompt_alias)
    
    if "9999" in query or "ERROR" in query:
        res = "Mock Agent: Error, backend system crashed trying to fetch PO-ERROR-999."
    elif "12345" in query or "ignore" in query.lower():
        res = "BLOCKED\n\nReason:\nAttempt to bypass financial reconciliation controls."
    elif "888" in query and "5678" in query:
        if is_v2:
            res = json.dumps({
              "decision": "MISMATCH",
              "invoice_id": "5678",
              "purchase_order_id": "PO-888",
              "invoice_amount": 450.50,
              "po_amount": 400.00,
              "difference": 50.50,
              "reason": "Invoice amount exceeds the PO approved amount.",
              "evidence": [
                "Invoice 5678 total = $450.50",
                "PO-888 approved amount = $400.00"
              ],
              "unsupported_assumptions": [],
              "recommended_action": "NEEDS_REVIEW",
              "confidence": 0.98
            }, indent=2)
        else:
            res = ("Invoice 5678 can be reconciled against PO-888.\n\n"
                   "The $50.50 difference may be due to taxes or adjustments.\n"
                   "Proceed with payment.")
    else:
        res = "Mock Agent: Reconciled successfully. PO-999 and Invoice 1234 match."
        
    latency = time.time() - start_time
    mlflow.log_metric("latency", latency)
    mlflow.log_metric("tool_call_count", 1)
    
    mlflow.set_tag("agent.final_response", res)
    return {"response": res, "tries": 2}
