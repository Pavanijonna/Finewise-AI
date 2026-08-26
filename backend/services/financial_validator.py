import math
from typing import Dict, Any, List

def validate_financial_consistency(
    loan_amount: float,
    interest_rate: float,
    tenure_months: int,
    emi: float,
    total_interest: float = 0.0,
    total_repayment: float = 0.0,
    processing_fee: float = 0.0
) -> Dict[str, Any]:
    """
    Validates cross-field mathematical consistency between extracted & calculated loan metrics.
    Flag 'Verification Required' if inconsistent or out of standard boundary bounds.
    """
    issues = []
    status = "VERIFIED"

    # 1. Basic Validity Bounds Checks
    if loan_amount <= 0:
        issues.append("Invalid or missing Loan Amount (Principal must be > 0).")
    if interest_rate < 0 or interest_rate > 50:
        issues.append(f"Interest rate of {interest_rate}% is outside standard market bounds (0% - 50%).")
    if tenure_months <= 0 or tenure_months > 480:
        issues.append(f"Loan tenure of {tenure_months} months is outside standard bounds (1 - 480 months).")

    # 2. EMI Consistency Check
    if loan_amount > 0 and interest_rate > 0 and tenure_months > 0 and emi > 0:
        r = (interest_rate / 100) / 12
        n = tenure_months
        theoretical_emi = loan_amount * r * math.pow(1 + r, n) / (math.pow(1 + r, n) - 1)
        
        # Allow 5% tolerance for rounding or fee inclusions
        diff_pct = abs(emi - theoretical_emi) / theoretical_emi
        if diff_pct > 0.05:
            issues.append(
                f"Extracted EMI (₹ {emi:,.2f}) deviates by {diff_pct*100:.1f}% from theoretically expected EMI (₹ {theoretical_emi:,.2f})."
            )

    # 3. Total Repayment Consistency Check: EMI * tenure approx matches Principal + Interest
    if emi > 0 and tenure_months > 0:
        computed_total_repay = emi * tenure_months
        if total_repayment > 0:
            repay_diff = abs(total_repayment - computed_total_repay) / max(1.0, computed_total_repay)
            if repay_diff > 0.05:
                issues.append(
                    f"Extracted Total Repayment (₹ {total_repayment:,.2f}) conflicts with EMI * Tenure calculation (₹ {computed_total_repay:,.2f})."
                )

        if total_interest > 0 and loan_amount > 0:
            expected_interest = computed_total_repay - loan_amount
            interest_diff = abs(total_interest - expected_interest) / max(1.0, expected_interest)
            if interest_diff > 0.08:
                issues.append(
                    f"Extracted Total Interest (₹ {total_interest:,.2f}) conflicts with Total Repayment - Principal (₹ {expected_interest:,.2f})."
                )

    # 4. Processing Fee Bounds Check
    if processing_fee > 0 and loan_amount > 0:
        fee_pct = (processing_fee / loan_amount) * 100
        if fee_pct > 10.0:
            issues.append(f"High upfront processing fee of {fee_pct:.1f}% (₹ {processing_fee:,.2f}) exceeds normal 0.5% - 3.0% threshold.")

    if issues:
        status = "VERIFICATION_REQUIRED"

    return {
        "validation_status": status,
        "is_valid": status == "VERIFIED",
        "issues": issues,
        "summary_message": "All extracted financial metrics are consistent." if status == "VERIFIED" else f"Verification Required: {len(issues)} consistency conflict(s) detected."
    }
