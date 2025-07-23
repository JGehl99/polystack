from flask import request, jsonify, send_file
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from jinja2 import Template
import io
import os
from datetime import datetime


# Jinja2 template for invoice data structure
INVOICE_TEMPLATE = """
{
    "company_name": "{{ company_name }}",
    "company_address": "{{ company_address }}",
    "invoice_number": "{{ invoice_number }}",
    "invoice_date": "{{ invoice_date }}",
    "due_date": "{{ due_date }}",
    "customer_name": "{{ customer_name }}",
    "customer_email": "{{ customer_email }}",
    "billing_address": "{{ billing_address }}",
    "shipping_address": "{{ shipping_address }}",
    "items": {{ items }},
    "subtotal": {{ subtotal }},
    "tax_rate": {{ tax_rate }},
    "tax_amount": {{ tax_amount }},
    "total": {{ total }},
    "notes": "{{ notes }}"
}
"""

def create_invoice_pdf(invoice_data):
    """Generate PDF invoice from invoice data"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=TA_LEFT
    )
    
    # Title
    title = Paragraph("PolyStack Invoice", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Company info and invoice details in two columns
    company_info = f"""
    <b>{invoice_data['company_name']}</b><br/>
    {invoice_data['company_address'].replace('\n', '<br/>')}
    """
    
    invoice_details = f"""
    <b>Invoice #:</b> {invoice_data['invoice_number']}<br/>
    <b>Date:</b> {invoice_data['invoice_date']}<br/>
    <b>Due Date:</b> {invoice_data['due_date']}
    """
    
    header_table = Table([
        [Paragraph(company_info, header_style), Paragraph(invoice_details, header_style)]
    ], colWidths=[3*inch, 3*inch])
    
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 24))
    
    # Customer info
    customer_info = f"""
    <b>Bill To:</b><br/>
    {invoice_data['customer_name']}<br/>
    {invoice_data['customer_email']}<br/>
    {invoice_data['billing_address'].replace('\n', '<br/>')}
    """
    
    shipping_info = f"""
    <b>Ship To:</b><br/>
    {invoice_data['shipping_address'].replace('\n', '<br/>')}
    """
    
    customer_table = Table([
        [Paragraph(customer_info, header_style), Paragraph(shipping_info, header_style)]
    ], colWidths=[3*inch, 3*inch])
    
    customer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(customer_table)
    elements.append(Spacer(1, 24))
    
    # Items table
    items_data = [['Description', 'Quantity', 'Unit Price', 'Total']]
    
    for item in invoice_data['items']:
        items_data.append([
            item['description'],
            str(item['quantity']),
            f"${item['unit_price']:.2f}",
            f"${item['total']:.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Description left-aligned
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(items_table)
    elements.append(Spacer(1, 24))
    
    # Totals table
    totals_data = [
        ['Subtotal:', f"${invoice_data['subtotal']:.2f}"],
        [f"Tax ({invoice_data['tax_rate']}%):", f"${invoice_data['tax_amount']:.2f}"],
        ['Total:', f"${invoice_data['total']:.2f}"]
    ]
    
    totals_table = Table(totals_data, colWidths=[4*inch, 1*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
    ]))
    
    elements.append(totals_table)
    
    # Notes
    if invoice_data.get('notes'):
        elements.append(Spacer(1, 24))
        notes_title = Paragraph("<b>Notes:</b>", header_style)
        notes_content = Paragraph(invoice_data['notes'], styles['Normal'])
        elements.append(notes_title)
        elements.append(notes_content)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def gen_invoice(data):
    """Generate invoice PDF from JSON data and save to file system"""
    try:
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Create Jinja2 template
        template = Template(INVOICE_TEMPLATE)
        
        # Set defaults for missing fields
        defaults = {
            'company_name': 'Your Company',
            'company_address': 'Your Address',
            'invoice_number': f"INV-{uuid.uuid4()}",
            'invoice_date': datetime.now().strftime('%Y-%m-%d'),
            'due_date': datetime.now().strftime('%Y-%m-%d'),
            'customer_name': 'Customer Name',
            'customer_email': 'customer@example.com',
            'billing_address': 'Billing Address',
            'shipping_address': 'Shipping Address',
            'items': [],
            'subtotal': 0.0,
            'tax_rate': 0.0,
            'tax_amount': 0.0,
            'total': 0.0,
            'notes': ''
        }
        
        # Merge defaults with provided data
        invoice_data = {**defaults, **data}
        
        # Calculate totals if items are provided but totals aren't
        if invoice_data['items'] and not data.get('subtotal'):
            subtotal = sum(item.get('total', item.get('quantity', 0) * item.get('unit_price', 0)) for item in invoice_data['items'])
            tax_amount = subtotal * (invoice_data['tax_rate'] / 100)
            total = subtotal + tax_amount
            
            invoice_data['subtotal'] = subtotal
            invoice_data['tax_amount'] = tax_amount
            invoice_data['total'] = total
        
        # Generate PDF
        pdf_buffer = create_invoice_pdf(invoice_data)
        
        # Create invoices directory if it doesn't exist
        invoices_dir = os.path.join(os.getcwd(), 'invoices')
        os.makedirs(invoices_dir, exist_ok=True)
        
        # Save PDF to file system
        # Sanitize the invoice_number to prevent path traversal
        sanitized_invoice_number = re.sub(r'[^a-zA-Z0-9_-]', '_', invoice_data['invoice_number'])
        filename = f"invoice_{sanitized_invoice_number}.pdf"
        filepath = os.path.join(invoices_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        # Return success response with file info
        return jsonify({
            "success": True,
            "message": "Invoice generated successfully",
            "filename": filename,
            "filepath": filepath,
            "invoice_number": invoice_data['invoice_number'],
            "total": invoice_data['total']
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

