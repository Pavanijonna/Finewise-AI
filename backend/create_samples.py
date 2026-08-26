import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_docs")
os.makedirs(SAMPLE_DIR, exist_ok=True)

docs = [
    {
        "filename": "hdfc_personal_loan.pdf",
        "title": "HDFC BANK PERSONAL LOAN AGREEMENT",
        "text": """HDFC BANK PERSONAL LOAN AGREEMENT
Borrower Name: Rahul Sharma
Sanctioned Loan Amount: INR 5,00,000 (Rupees Five Lakhs Only)
Annual Rate of Interest: 11.5% per annum (Fixed Interest Rate)
Repayment Period: 60 Months (5 Years)
Equated Monthly Instalment (EMI): INR 11,000 per month
Processing Fee: INR 2,500 upfront administrative fee
Payment Due Date: 5th day of every calendar month

TERMS AND CONDITIONS & FINANCIAL CLAUSES:
1. INTEREST RATE STRUCTURE: The loan carries a Fixed Rate of Interest of 11.5% p.a., which shall remain unchanged throughout the 60-month loan tenure.
2. PREPAYMENT & FORECLOSURE CHARGES: Borrower may foreclose or prepay the loan after completing 12 monthly instalments. Foreclosure penalty of 3% + GST on the outstanding principal balance will be levied.
3. OVERDUE & LATE PAYMENT PENALTY: Delayed EMI payments will incur penal interest of 2% per month (24% per annum) on the overdue instalment amount along with a cheque bounce charge of INR 500 per instance.
4. LOAN PROTECTION INSURANCE: Borrower agrees to enroll in Credit Shield Insurance with a single premium of INR 4,200 added to the principal."""
    },
    {
        "filename": "sbi_home_loan.pdf",
        "title": "STATE BANK OF INDIA HOME LOAN SANCTION LETTER",
        "text": """STATE BANK OF INDIA - HOME LOAN SANCTION LETTER
Borrower Name: Priya Patel
Sanctioned Loan Amount: INR 35,00,000 (Rupees Thirty Five Lakhs Only)
Annual Rate of Interest: 8.40% per annum (Floating MCLR Linked Interest Rate)
Repayment Period: 240 Months (20 Years)
Equated Monthly Instalment (EMI): INR 30,150 per month
Processing Fee: INR 3,500 legal & valuation charges
Payment Due Date: 10th day of every calendar month

TERMS AND CONDITIONS & FINANCIAL CLAUSES:
1. INTEREST RATE STRUCTURE: Interest rate is Floating, linked to SBI 1-Year MCLR rate. The interest rate is subject to reset every 12 months based on RBI monetary policy announcements.
2. PREPAYMENT & FORECLOSURE CHARGES: Zero Foreclosure Charges. As per RBI guidelines for floating rate home loans, NO prepayment or foreclosure penalty shall be charged to individual borrowers.
3. OVERDUE & LATE PAYMENT PENALTY: Overdue EMI payments will attract penal charges at 1.5% per month on the defaulted amount.
4. PROPERTY INSURANCE: Mandatory property and fire insurance coverage required for the mortgaged property throughout the tenure."""
    },
    {
        "filename": "axis_car_loan.pdf",
        "title": "AXIS BANK AUTO LOAN AGREEMENT",
        "text": """AXIS BANK AUTO LOAN AGREEMENT
Borrower Name: Amit Vikram
Sanctioned Loan Amount: INR 8,50,000 (Rupees Eight Lakh Fifty Thousand Only)
Annual Rate of Interest: 9.75% per annum (Fixed Rate)
Repayment Period: 84 Months (7 Years)
Equated Monthly Instalment (EMI): INR 14,025 per month
Processing Fee: INR 1,500 promotional administrative fee
Payment Due Date: 7th day of every calendar month

TERMS AND CONDITIONS & FINANCIAL CLAUSES:
1. INTEREST RATE STRUCTURE: Fixed interest rate at 9.75% per annum for the complete 84 months duration.
2. PREPAYMENT & FORECLOSURE CHARGES: Prepayment allowed after 6 months. Prepayment charge of 2% on the prepaid amount if closed within 24 months, 1% thereafter.
3. OVERDUE & LATE PAYMENT PENALTY: Penal interest of 2% per month on overdue EMI installments.
4. VEHICLE HYPOTHECATION: The vehicle remains hypothecated to Axis Bank until full repayment and issuance of No Objection Certificate (NOC)."""
    }
]

def make_sample_pdfs():
    styles = getSampleStyleSheet()
    for d in docs:
        pdf_path = os.path.join(SAMPLE_DIR, d["filename"])
        txt_path = os.path.join(SAMPLE_DIR, d["filename"].replace(".pdf", ".txt"))
        
        # Write text version
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(d["text"])
            
        # Write PDF version using ReportLab
        pdf = SimpleDocTemplate(pdf_path, pagesize=letter)
        story = [
            Paragraph(f"<b>{d['title']}</b>", styles['Heading1']),
            Spacer(1, 15)
        ]
        for line in d["text"].strip().split("\n"):
            if line.strip():
                story.append(Paragraph(line.strip(), styles['Normal']))
                story.append(Spacer(1, 4))
        pdf.build(story)
        print(f"Created valid binary PDF: {pdf_path}")

if __name__ == "__main__":
    make_sample_pdfs()
