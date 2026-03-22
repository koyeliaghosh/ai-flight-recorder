import mlflow
from src.sample_data import INVOICES, PURCHASE_ORDERS, SUPPLIERS

@mlflow.trace(name="get_invoice_details")
def get_invoice_details(invoice_id: str) -> dict:
    """Retrieve details for a specific invoice by its ID."""
    return INVOICES.get(invoice_id, {"error": "Invoice not found"})

@mlflow.trace(name="get_purchase_order_details")
def get_purchase_order_details(po_id: str) -> dict:
    """Retrieve details for a specific purchase order by its ID."""
    return PURCHASE_ORDERS.get(po_id, {"error": "PO not found"})

@mlflow.trace(name="get_supplier_info")
def get_supplier_info(supplier_id: str) -> dict:
    """Retrieve details and trust score for a specific supplier by ID."""
    return SUPPLIERS.get(supplier_id, {"error": "Supplier not found"})
