import os
import json
import mlflow
from typing import Optional

# Using Vertex AI SDK
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part

from src.retrieval import get_invoice_details, get_purchase_order_details, get_supplier_info

# Initialize Vertex AI globally if possible. For local fast PoC, we will wrap in try-except.
try:
    # Requires GOOGLE_APPLICATION_CREDENTIALS or gcloud auth application-default login
    vertexai.init(project=os.environ.get("GOOGLE_CLOUD_PROJECT", "my-project"), location="us-central1")
    VERTEX_AVAILABLE = True
except Exception as e:
    print(f"Warning: Vertex AI not initialized. {e}")
    VERTEX_AVAILABLE = False

# Define tool declarations for Vertex Gemini
get_invoice_func = FunctionDeclaration(
    name="get_invoice_details",
    description="Retrieve details for a specific invoice by its ID",
    parameters={
        "type": "object",
        "properties": {"invoice_id": {"type": "string"}},
        "required": ["invoice_id"]
    }
)

get_po_func = FunctionDeclaration(
    name="get_purchase_order_details",
    description="Retrieve details for a specific purchase order by its ID",
    parameters={
        "type": "object",
        "properties": {"po_id": {"type": "string"}},
        "required": ["po_id"]
    }
)

get_supplier_func = FunctionDeclaration(
    name="get_supplier_info",
    description="Retrieve details and trust score for a specific supplier by ID",
    parameters={
        "type": "object",
        "properties": {"supplier_id": {"type": "string"}},
        "required": ["supplier_id"]
    }
)

finance_tool = Tool(
    function_declarations=[get_invoice_func, get_po_func, get_supplier_func]
)

# Registry for actual python functions matching the declarations
FUNC_MAP = {
    "get_invoice_details": get_invoice_details,
    "get_purchase_order_details": get_purchase_order_details,
    "get_supplier_info": get_supplier_info
}

@mlflow.trace(name="run_reconciliation_agent")
def run_agent(query: str, prompt_version: str = "v1", max_tries: int = 2) -> dict:
    """
    Core agent execution function with a strict max_tries limit.
    Traced heavily by MLflow.
    """
    mlflow.log_param("query", query)
    mlflow.log_param("prompt_version", prompt_version)
    mlflow.log_param("max_tries", max_tries)
    
    # Simple simulated fallback for instant PoC running if Vertex fails to load
    if not VERTEX_AVAILABLE:
        mlflow.log_param("mode", "mock_fallback")
        return {"response": "Mock fallback: Discrepancy found. Vertex AI credentials not detected.", "tries": 1}
    
    system_prompt = f"You are an AI Invoice Reconciliation Agent (Prompt Version {prompt_version}). Use tools to check invoices against POs."
    
    # Initialize the model instance with tools and system prompt per run
    model = GenerativeModel(
        "gemini-1.5-flash-001",
        tools=[finance_tool],
        system_instruction=[system_prompt]
    )
    chat = model.start_chat()
    
    current_try = 0
    message = query
    final_response = ""
    
    # Set strict 2-try limit
    while current_try < max_tries:
        current_try += 1
        
        # Call model
        response = chat.send_message(message)
        
        if not response.candidates:
            final_response = "No response from model."
            break
            
        function_calls = response.candidates[0].function_calls
        
        if not function_calls:
            # Model generated a text response and is done
            final_response = response.text
            break
            
        # Execute tool calls
        tool_responses = []
        for function_call in function_calls:
            func_name = function_call.name
            args = {k: v for k, v in function_call.args.items()}
            
            if func_name in FUNC_MAP:
                result = FUNC_MAP[func_name](**args)
                tool_responses.append(Part.from_function_response(
                    name=func_name,
                    response={"result": result}
                ))
            else:
                tool_responses.append(Part.from_function_response(
                    name=func_name,
                    response={"error": "Tool not found"}
                ))
        
        # Send tool results back to the model
        message = tool_responses
    
    if current_try >= max_tries and not final_response:
        final_response = "Agent aborted: Reached strict max_tries limit of 2."
        
    mlflow.log_metric("total_agent_tries", current_try)
    mlflow.set_tag("agent.final_response", final_response)
    
    return {
        "response": final_response,
        "tries": current_try
    }
