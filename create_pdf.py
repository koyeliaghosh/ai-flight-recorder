import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_invoice_pdf():
    os.makedirs("data", exist_ok=True)
    c = canvas.Canvas("data/invoice_5678.pdf", pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Invoice #5678")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 700, "Supplier: ABC Manufacturing")
    c.drawString(50, 675, "Purchase Order: PO-888")
    c.drawString(50, 650, "Invoice Amount: $450.50")
    
    c.save()
    print("PDF generated successfully.")

if __name__ == "__main__":
    create_invoice_pdf()
