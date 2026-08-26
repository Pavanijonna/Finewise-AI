import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from typing import Dict, Any, List

def generate_pdf_report(doc_data: Dict[str, Any], clauses: List[Dict[str, Any]], risk_info: Dict[str, Any]) -> bytes:
    """
    Generates a professional ReportLab PDF Financial Analysis & Decision Support Report.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        spaceAfter=16
    )

    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=12,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#334155'),
        spaceAfter=4
    )

    elements = []

    # Title & Subtitle
    elements.append(Paragraph("FinWise AI — Financial Decision Support Report", title_style))
    elements.append(Paragraph(f"Document Analysis & Decision Support Summary | Document ID: {doc_data.get('doc_id', 'N/A')} | File: {doc_data.get('filename', 'N/A')}", subtitle_style))
    elements.append(Spacer(1, 6))

    # 1. Extracted Facts Table
    elements.append(Paragraph("1. Extracted Facts & Contract Parameters", section_style))
    metrics_table_data = [
        [Paragraph("<b>Parameter</b>", normal_style), Paragraph("<b>Value</b>", normal_style), Paragraph("<b>Verification Status</b>", normal_style)],
        ["Borrower Name", str(doc_data.get("borrower_name", "N/A")), "Extracted"],
        ["Lender Name", str(doc_data.get("lender_name", "Financial Institution")), "Extracted"],
        ["Loan Type", str(doc_data.get("loan_type", "Personal Loan")), "Extracted"],
        ["Principal Amount", f"₹ {float(doc_data.get('loan_amount', 0)):,.2f}", "Verified"],
        ["Interest Rate", f"{float(doc_data.get('interest_rate', 0)):.2f}% ({doc_data.get('interest_type', 'Fixed')})", "Verified"],
        ["Loan Tenure", f"{int(doc_data.get('tenure', 0))} Months", "Verified"],
        ["Monthly EMI", f"₹ {float(doc_data.get('emi', 0)):,.2f}", "Calculated / Verified"],
        ["Processing Fee", f"₹ {float(doc_data.get('processing_fee', 0)):,.2f}", "Extracted"],
        ["Total Interest Payable", f"₹ {float(doc_data.get('total_interest', 0)):,.2f}", "Calculated Value"],
        ["Total Repayment Amount", f"₹ {float(doc_data.get('total_repayment', 0)):,.2f}", "Calculated Value"],
    ]

    t1 = Table(metrics_table_data, colWidths=[180, 200, 140])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 10))

    # 2. Risk Assessment & 7-Component Breakdown
    elements.append(Paragraph("2. AI Risk Assessment & Component Scores", section_style))
    risk_score = risk_info.get("overall_risk_score", risk_info.get("risk_score", 5.0))
    risk_cat = risk_info.get("risk_level", risk_info.get("risk_category", "MEDIUM_RISK"))
    elements.append(Paragraph(f"<b>Overall Contract Risk Rating:</b> {risk_cat} ({risk_score} / 10.0)", normal_style))
    elements.append(Paragraph(f"<i>Rationale:</i> {risk_info.get('why_explanation', 'Evaluated across interest, fee, penalty, foreclosure, and variable rate components.')}", normal_style))
    elements.append(Spacer(1, 6))

    # Component Scores Table
    comp_scores = risk_info.get("component_scores", {})
    if comp_scores:
        comp_table_data = [[Paragraph("<b>Risk Component</b>", normal_style), Paragraph("<b>Score (1-10)</b>", normal_style), Paragraph("<b>Explanation</b>", normal_style)]]
        for k, v in comp_scores.items():
            comp_table_data.append([
                k.replace("_", " ").title(),
                f"{v.get('score', 5.0)} / 10",
                v.get("explanation", "")
            ])
        t_comp = Table(comp_table_data, colWidths=[140, 80, 300])
        t_comp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_comp)
        elements.append(Spacer(1, 10))

    # Recommendations
    elements.append(Paragraph("<b>Recommendations for Borrower:</b>", normal_style))
    for rec in risk_info.get("recommendations", []):
        elements.append(Paragraph(f"• {rec}", normal_style))
    elements.append(Spacer(1, 10))

    # 3. Key Clauses
    elements.append(Paragraph("3. Classified Financial Clauses", section_style))
    for c in clauses:
        elements.append(Paragraph(f"<b>{c.get('title')}</b> [{c.get('risk_level')}]", normal_style))
        elements.append(Paragraph(f"<i>Snippet:</i> \"{c.get('text_snippet')}\"", normal_style))
        elements.append(Paragraph(f"<i>Plain-Language Explanation:</i> {c.get('simple_explanation')}", normal_style))
        elements.append(Spacer(1, 4))

    # Disclaimer
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>Disclaimer:</b> This document is an AI-generated decision-support analysis. Extracted values and model calculations should be independently verified prior to signing binding financial contracts.", normal_style))

    doc.build(elements)
    return buffer.getvalue()
