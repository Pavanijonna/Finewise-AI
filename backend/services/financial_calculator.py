import math
from typing import Dict, Any, List

def calculate_loan_financials(
    loan_amount: float,
    annual_interest_rate: float,
    tenure_months: int,
    processing_fee: float = 0.0,
    emi_override: float = 0.0
) -> Dict[str, Any]:
    """
    Computes precise financial calculations for loan decision support:
    - Monthly EMI
    - Total Interest Payable
    - Total Repayment Amount
    - Effective APR (combining interest rate & amortized upfront fee)
    - Full Amortization Schedule (Month, Beginning Balance, EMI, Principal Component, Interest Component, Ending Balance)
    """
    if loan_amount <= 0 or tenure_months <= 0:
        return {
            "loan_amount": max(0.0, loan_amount),
            "annual_interest_rate": max(0.0, annual_interest_rate),
            "tenure_months": max(0, tenure_months),
            "calculated_emi": 0.0,
            "total_interest_payable": 0.0,
            "total_repayment_amount": 0.0,
            "processing_fee": max(0.0, processing_fee),
            "processing_fee_percentage": 0.0,
            "effective_apr": max(0.0, annual_interest_rate),
            "amortization_schedule": []
        }

    monthly_rate = (annual_interest_rate / 100) / 12 if annual_interest_rate > 0 else 0.0

    if emi_override and emi_override > 0:
        emi = emi_override
    else:
        if monthly_rate > 0:
            pow_val = math.pow(1 + monthly_rate, tenure_months)
            emi = loan_amount * monthly_rate * pow_val / (pow_val - 1)
        else:
            emi = loan_amount / tenure_months

    emi = round(emi, 2)
    total_repayment = round(emi * tenure_months, 2)
    total_interest = round(max(0.0, total_repayment - loan_amount), 2)
    
    processing_fee_pct = round((processing_fee / loan_amount) * 100, 2) if loan_amount > 0 else 0.0
    
    # Effective APR approximation: Nominal Rate + (Upfront Fee % / Tenure in years)
    tenure_years = tenure_months / 12.0
    effective_apr = round(annual_interest_rate + (processing_fee_pct / tenure_years if tenure_years > 0 else 0.0), 2)

    schedule = []
    balance = loan_amount
    for month in range(1, tenure_months + 1):
        beginning_balance = balance
        interest_for_month = round(beginning_balance * monthly_rate, 2)
        principal_for_month = round(emi - interest_for_month, 2)

        if month == tenure_months:
            principal_for_month = round(beginning_balance, 2)
            actual_emi = round(principal_for_month + interest_for_month, 2)
            ending_balance = 0.0
        else:
            ending_balance = round(max(0.0, beginning_balance - principal_for_month), 2)
            actual_emi = emi

        balance = ending_balance

        schedule.append({
            "month": month,
            "beginning_balance": beginning_balance,
            "installment": actual_emi,
            "principal_component": principal_for_month,
            "interest_component": interest_for_month,
            "ending_balance": ending_balance,
            "remaining_balance": ending_balance
        })

    return {
        "loan_amount": loan_amount,
        "annual_interest_rate": annual_interest_rate,
        "tenure_months": tenure_months,
        "calculated_emi": emi,
        "total_interest_payable": total_interest,
        "total_repayment_amount": total_repayment,
        "processing_fee": processing_fee,
        "processing_fee_percentage": processing_fee_pct,
        "effective_apr": effective_apr,
        "amortization_schedule": schedule
    }
