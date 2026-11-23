import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def create_sample_invoices(output_dir="sample_invoices"):
    os.makedirs(output_dir, exist_ok=True)
    styles = getSampleStyleSheet()

    # Custom styles
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        fontName='Helvetica'
    )
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        fontName='Helvetica-Bold'
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        fontName='Helvetica'
    )
    right_body = ParagraphStyle(
        'RightBody',
        parent=body_style,
        alignment=TA_RIGHT
    )
    right_bold = ParagraphStyle(
        'RightBold',
        parent=header_style,
        alignment=TA_RIGHT
    )

    # -------------------------------------------------------------
    # Invoice 1: Acme Design & Smart Contract Consulting
    # -------------------------------------------------------------
    pdf_path_1 = os.path.join(output_dir, "invoice_apex_design_101.pdf")
    doc1 = SimpleDocTemplate(pdf_path_1, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements1 = []

    # Header section
    header_data = [
        [
            Paragraph("<b>APEX CREATIVE LABS</b><br/><font color='#64748B'>Web3 Architecture & Design</font>", header_style),
            Paragraph("<b>INVOICE</b><br/><font color='#4F46E5'><b>#INV-2026-00101</b></font>", right_bold)
        ]
    ]
    t_header = Table(header_data, colWidths=[300, 230])
    t_header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements1.append(t_header)
    elements1.append(Spacer(1, 15))
    elements1.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#E2E8F0'), spaceAfter=15))

    # Meta section
    meta_data = [
        [
            Paragraph("<b>Billed From:</b><br/>Apex Creative Labs LLC<br/>100 Innovation Blvd, Suite 400<br/>San Francisco, CA 94105<br/>billing@apexcreative.io", body_style),
            Paragraph("<b>Billed To:</b><br/>Acme Global Enterprises<br/>742 Evergreen Terrace<br/>Seattle, WA 98101<br/>accounts@acmeglobal.com", body_style),
            Paragraph("<b>Invoice Details:</b><br/>Issue Date: Nov 20, 2026<br/>Due Date: Dec 04, 2026<br/>Payment Terms: Net 14<br/>Currency: USD ($)", body_style)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[180, 180, 170])
    t_meta.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements1.append(t_meta)
    elements1.append(Spacer(1, 20))

    # Line Items
    items_data = [
        [Paragraph("<b>Description</b>", header_style), Paragraph("<b>Hours</b>", header_style), Paragraph("<b>Rate</b>", right_bold), Paragraph("<b>Amount</b>", right_bold)],
        [Paragraph("Frontend UI/UX Architecture & dApp Prototyping", body_style), "40.0", "$125.00", "$5,000.00"],
        [Paragraph("Gno.land Smart Contract Integration & Security Hardening", body_style), "25.0", "$150.00", "$3,750.00"],
        [Paragraph("Decentralized Vault ABCI Query RPC Integration", body_style), "12.0", "$125.00", "$1,500.00"],
        [Paragraph("Automated End-to-End Test Suite & Verification Module", body_style), "8.0", "$100.00", "$800.00"],
    ]
    t_items = Table(items_data, colWidths=[280, 70, 80, 100])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
    ]))
    elements1.append(t_items)
    elements1.append(Spacer(1, 15))

    # Summary table
    summary_data = [
        ["", "", Paragraph("Subtotal:", right_body), Paragraph("$11,050.00", right_body)],
        ["", "", Paragraph("Tax (8.25%):", right_body), Paragraph("$911.63", right_body)],
        ["", "", Paragraph("<b>Total Due:</b>", right_bold), Paragraph("<b>$11,961.63</b>", right_bold)],
    ]
    t_summary = Table(summary_data, colWidths=[200, 80, 150, 100])
    t_summary.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEABOVE', (2, 2), (3, 2), 1, colors.HexColor('#4F46E5')),
    ]))
    elements1.append(t_summary)
    elements1.append(Spacer(1, 25))

    # Footer note
    note = Paragraph(
        "<b>Notice:</b> This invoice is cryptographically fingerprinted using SHA-256 and anchored to the "
        "Gno.land blockchain registry (Invoice Fingerprint Vault). Any alteration of this document invalidates its authenticity.",
        subtitle_style
    )
    elements1.append(note)
    doc1.build(elements1)
    print(f"Generated: {pdf_path_1}")

    # -------------------------------------------------------------
    # Invoice 2: Cloud Infrastructure & Server Hosting Receipt
    # -------------------------------------------------------------
    pdf_path_2 = os.path.join(output_dir, "receipt_nexus_cloud_202.pdf")
    doc2 = SimpleDocTemplate(pdf_path_2, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements2 = []

    header_data2 = [
        [
            Paragraph("<b>NEXUS CLOUD INFRASTRUCTURE</b><br/><font color='#64748B'>High Performance Bare-Metal & RPC Nodes</font>", header_style),
            Paragraph("<b>PAYMENT RECEIPT</b><br/><font color='#10B981'><b>PAID #REC-2026-00202</b></font>", right_bold)
        ]
    ]
    t_header2 = Table(header_data2, colWidths=[310, 220])
    t_header2.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements2.append(t_header2)
    elements2.append(Spacer(1, 15))
    elements2.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#E2E8F0'), spaceAfter=15))

    meta_data2 = [
        [
            Paragraph("<b>Provider:</b><br/>Nexus Infrastructure Ltd.<br/>One Financial Plaza, Suite 1200<br/>Austin, TX 78701<br/>support@nexuscloud.io", body_style),
            Paragraph("<b>Customer:</b><br/>Gnome Tavern Development Team<br/>Hackathon Participant Account<br/>Billing ID: #CUST-9941", body_style),
            Paragraph("<b>Receipt Details:</b><br/>Payment Date: Nov 18, 2026<br/>Payment Method: Card ending 4419<br/>Status: <font color='#10B981'>Completed</font>", body_style)
        ]
    ]
    t_meta2 = Table(meta_data2, colWidths=[180, 180, 170])
    t_meta2.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements2.append(t_meta2)
    elements2.append(Spacer(1, 20))

    items_data2 = [
        [Paragraph("<b>Service Description</b>", header_style), Paragraph("<b>Qty</b>", header_style), Paragraph("<b>Unit Price</b>", right_bold), Paragraph("<b>Total</b>", right_bold)],
        [Paragraph("Dedicated Gno.land Onyx RPC Full Node (32GB RAM, 8 vCPU)", body_style), "1 mo", "$280.00", "$280.00"],
        [Paragraph("High-Speed NVMe Storage Tier 1 (1,000 GB Allocated)", body_style), "1,000 GB", "$0.12", "$120.00"],
        [Paragraph("Global Anycast Traffic & SSL Edge Scrubbing (5TB bandwidth)", body_style), "1 pkg", "$75.00", "$75.00"],
    ]
    t_items2 = Table(items_data2, colWidths=[280, 70, 80, 100])
    t_items2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
    ]))
    elements2.append(t_items2)
    elements2.append(Spacer(1, 15))

    summary_data2 = [
        ["", "", Paragraph("Subtotal:", right_body), Paragraph("$475.00", right_body)],
        ["", "", Paragraph("Applicable Tax (0.0%):", right_body), Paragraph("$0.00", right_body)],
        ["", "", Paragraph("<b>Amount Charged:</b>", right_bold), Paragraph("<b>$475.00 USD</b>", right_bold)],
    ]
    t_summary2 = Table(summary_data2, colWidths=[200, 80, 150, 100])
    t_summary2.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEABOVE', (2, 2), (3, 2), 1, colors.HexColor('#10B981')),
    ]))
    elements2.append(t_summary2)
    elements2.append(Spacer(1, 25))

    note2 = Paragraph(
        "<b>Electronic Receipt Proof:</b> This official receipt is certified and can be independently verified on the "
        "Invoice Fingerprint Vault. Tamper-evident verification guarantee.",
        subtitle_style
    )
    elements2.append(note2)
    doc2.build(elements2)
    print(f"Generated: {pdf_path_2}")

    # -------------------------------------------------------------
    # Invoice 3: Freelance Protocol Engineering Retainer
    # -------------------------------------------------------------
    pdf_path_3 = os.path.join(output_dir, "contract_retainer_zenith_303.pdf")
    doc3 = SimpleDocTemplate(pdf_path_3, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements3 = []

    header_data3 = [
        [
            Paragraph("<b>ZENITH PROTOCOL LABS</b><br/><font color='#64748B'>Decentralized Infrastructure & Auditing</font>", header_style),
            Paragraph("<b>RETAINER INVOICE</b><br/><font color='#6366F1'><b>#RET-2026-00303</b></font>", right_bold)
        ]
    ]
    t_header3 = Table(header_data3, colWidths=[310, 220])
    t_header3.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements3.append(t_header3)
    elements3.append(Spacer(1, 15))
    elements3.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#E2E8F0'), spaceAfter=15))

    meta_data3 = [
        [
            Paragraph("<b>Consultant:</b><br/>Zenith Protocol Labs<br/>Bahnhofstrasse 24<br/>6300 Zug, Switzerland<br/>contact@zenithlabs.ch", body_style),
            Paragraph("<b>Client:</b><br/>FinTech Global Capital AG<br/>Paradeplatz 8<br/>8001 Zurich, Switzerland<br/>legal@fintechglobal.ch", body_style),
            Paragraph("<b>Terms:</b><br/>Billing Period: Nov 2026<br/>Invoice Date: Nov 01, 2026<br/>Due Date: Nov 15, 2026<br/>Currency: CHF", body_style)
        ]
    ]
    t_meta3 = Table(meta_data3, colWidths=[180, 180, 170])
    t_meta3.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements3.append(t_meta3)
    elements3.append(Spacer(1, 20))

    items_data3 = [
        [Paragraph("<b>Deliverable Description</b>", header_style), Paragraph("<b>Unit</b>", header_style), Paragraph("<b>Rate (CHF)</b>", right_bold), Paragraph("<b>Total (CHF)</b>", right_bold)],
        [Paragraph("Core Protocol Consensus Engineering & Realm Optimization", body_style), "1 mo", "9,500.00", "9,500.00"],
        [Paragraph("Smart Contract Security Verification & Formal Methods Audit", body_style), "Milestone 1", "5,200.00", "5,200.00"],
        [Paragraph("Zero-Knowledge & Deterministic State Proof Consulting", body_style), "20 hrs", "225.00", "4,500.00"],
    ]
    t_items3 = Table(items_data3, colWidths=[280, 70, 80, 100])
    t_items3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
    ]))
    elements3.append(t_items3)
    elements3.append(Spacer(1, 15))

    summary_data3 = [
        ["", "", Paragraph("Subtotal:", right_body), Paragraph("19,200.00 CHF", right_body)],
        ["", "", Paragraph("Swiss VAT (7.7%):", right_body), Paragraph("1,478.40 CHF", right_body)],
        ["", "", Paragraph("<b>Total Payable:</b>", right_bold), Paragraph("<b>20,678.40 CHF</b>", right_bold)],
    ]
    t_summary3 = Table(summary_data3, colWidths=[200, 80, 150, 100])
    t_summary3.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEABOVE', (2, 2), (3, 2), 1, colors.HexColor('#6366F1')),
    ]))
    elements3.append(t_summary3)
    elements3.append(Spacer(1, 25))

    note3 = Paragraph(
        "<b>Legal & Cryptographic Timestamp:</b> This contract retainer is registered with the Gno.land Proof-of-Existence "
        "Vault under SHA-256 digest certification. Valid upon on-chain block commitment.",
        subtitle_style
    )
    elements3.append(note3)
    doc3.build(elements3)
    print(f"Generated: {pdf_path_3}")

if __name__ == "__main__":
    create_sample_invoices()
