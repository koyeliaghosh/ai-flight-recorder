"""
Sample data for the Invoice Reconciliation use case.
This simulates a real enterprise database.
"""

INVOICES = {
    "1234": {
        "invoice_id": "1234",
        "supplier_id": "SUP-001",
        "total_amount": 1500.00,
        "date": "2023-10-01",
        "line_items": [
            {"item": "Server Rack", "quantity": 1, "price": 1000.00},
            {"item": "Network Switch", "quantity": 2, "price": 250.00}
        ]
    },
    "5678": {
        "invoice_id": "5678",
        "supplier_id": "SUP-002",
        "total_amount": 450.50,
        "date": "2023-10-05",
        "line_items": [
            {"item": "Office Chairs", "quantity": 3, "price": 150.16}
        ]
    }
}

PURCHASE_ORDERS = {
    "PO-999": {
        "po_id": "PO-999",
        "supplier_id": "SUP-001",
        "approved_amount": 1500.00,
        "status": "APPROVED"
    },
    "PO-888": {
        "po_id": "PO-888",
        "supplier_id": "SUP-002",
        "approved_amount": 400.00,  # Discrepancy! Invoice is 450.50
        "status": "APPROVED"
    }
}

SUPPLIERS = {
    "SUP-001": {"name": "TechHardware Inc.", "trust_score": 98},
    "SUP-002": {"name": "OfficeSupplies Co.", "trust_score": 85}
}
