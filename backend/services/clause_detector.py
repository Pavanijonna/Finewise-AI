import re
from typing import List, Dict, Any

def analyze_clauses(text: str) -> List[Dict[str, Any]]:
    """
    Scans contract text, classifies financial clauses into HIGH, MEDIUM, LOW risk categories,
    and provides simple plain-language explanations using cautious phrasing ('Potential financial concern').
    """
    detected_clauses = []

    # 1. Interest Rate Structure (Fixed vs Floating)
    if re.search(r'(?i)(?:floating|variable|reset|mclr|repo\s*rate|benchmark\s*rate)', text):
        snippet = _extract_matching_snippet(text, r'(?i)(?:floating|variable|reset|mclr|repo\s*rate)[^\.\n]+')
        detected_clauses.append({
            "title": "Floating Interest Rate Exposure",
            "clause_type": "Interest Rate Structure",
            "text_snippet": snippet or "Interest rate is benchmarked to bank repo/MCLR rates and subject to periodic adjustments.",
            "risk_level": "MEDIUM_RISK",
            "impact_score": 6.5,
            "simple_explanation": "Potential financial concern: Your interest rate is variable. If central bank interest rates rise, your monthly EMI or total loan tenure will automatically increase."
        })
    else:
        detected_clauses.append({
            "title": "Fixed Interest Rate Structure",
            "clause_type": "Interest Rate Structure",
            "text_snippet": "Interest rate is fixed for the entire duration of the loan tenure.",
            "risk_level": "LOW_RISK",
            "impact_score": 2.0,
            "simple_explanation": "Standard condition: Your interest rate and monthly EMI remain constant throughout the loan term, providing payment predictability."
        })

    # 2. Foreclosure & Prepayment Restrictions
    if re.search(r'(?i)(?:foreclosure|prepayment|early\s*settlement|early\s*closure)\s*(?:charge|penalty|fee)', text):
        snippet = _extract_matching_snippet(text, r'(?i)(?:foreclosure|prepayment|early\s*settlement)[^\.\n]+')
        risk = "HIGH_RISK" if any(kw in snippet.lower() for kw in ["3%", "4%", "5%", "prohibited", "lock-in", "penalty"]) else "MEDIUM_RISK"
        detected_clauses.append({
            "title": "Prepayment & Foreclosure Charge",
            "clause_type": "Foreclosure Conditions",
            "text_snippet": snippet or "Borrower will incur a foreclosure fee of 3% on outstanding balance if loan is closed prior to maturity.",
            "risk_level": risk,
            "impact_score": 8.0 if risk == "HIGH_RISK" else 5.5,
            "simple_explanation": f"Potential financial concern ({risk.replace('_', ' ')}): Early repayment of the loan triggers a fee on the remaining balance. Check if lock-in periods apply."
        })
    else:
        detected_clauses.append({
            "title": "Standard Prepayment Terms",
            "clause_type": "Foreclosure Conditions",
            "text_snippet": "Prepayment permitted subject to standard guidelines.",
            "risk_level": "LOW_RISK",
            "impact_score": 2.5,
            "simple_explanation": "Ordinary administrative terms: Standard prepayment options available without restrictive lock-ins."
        })

    # 3. Late Payment Penalty & Aggressive Default Clauses
    if re.search(r'(?i)(?:late\s*payment|overdue|default\s*interest|penal\s*interest)', text):
        snippet = _extract_matching_snippet(text, r'(?i)(?:late\s*payment|overdue|penal\s*interest)[^\.\n]+')
        detected_clauses.append({
            "title": "Aggressive Penal Interest & Overdue Charge",
            "clause_type": "Late Payment Penalty",
            "text_snippet": snippet or "Penal interest of 2% per month will be levied on overdue instalments.",
            "risk_level": "HIGH_RISK",
            "impact_score": 8.5,
            "simple_explanation": "Potential financial concern: Missing a due date triggers steep penal interest (compounded up to 24% p.a.) in addition to dishonor charges."
        })

    # 4. Mandatory Credit Shield / Insurance Requirement
    if re.search(r'(?i)(?:insurance|credit\s*shield|loan\s*protector|property\s*insurance)', text):
        snippet = _extract_matching_snippet(text, r'(?i)(?:insurance|credit\s*shield|protector)[^\.\n]+')
        detected_clauses.append({
            "title": "Mandatory Loan Insurance Policy",
            "clause_type": "Insurance Requirement",
            "text_snippet": snippet or "Borrower must purchase loan protection insurance policy mandated by the lender.",
            "risk_level": "MEDIUM_RISK",
            "impact_score": 6.0,
            "simple_explanation": "Potential financial concern: The lender mandates a credit shield policy. Insurance premium costs are often bundled directly into the funded principal."
        })

    # 5. Administrative & Ancillary Charges
    if re.search(r'(?i)(?:administrative|legal|valuation|documentation|cheque\s*bounce|notice\s*charge)', text):
        snippet = _extract_matching_snippet(text, r'(?i)(?:administrative|legal|valuation|documentation|bounce)[^\.\n]+')
        detected_clauses.append({
            "title": "Ancillary & Administrative Fee Schedule",
            "clause_type": "Hidden Charges",
            "text_snippet": snippet or "Documentation, legal verification, and cheque bounce charges applicable as per fee schedule.",
            "risk_level": "MEDIUM_RISK",
            "impact_score": 5.5,
            "simple_explanation": "Potential financial concern: Ancillary fees (legal verification, documentation, cheque bounce fees) may be levied during loan execution or servicing."
        })

    return detected_clauses


def compute_component_risk_scores(
    clauses: List[Dict[str, Any]],
    extracted_data: Dict[str, Any] = None,
    weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    7-Component Transparent Risk Scoring Engine.
    Computes individual scores for:
    - Interest Risk
    - Fee Risk
    - Penalty Risk
    - Foreclosure Risk
    - Variable Rate Risk
    - Insurance Risk
    - Contract Complexity Risk

    Returns overall weighted score, risk level, component breakdowns, risk factors, evidence, and 'WHY' explanations.
    """
    extracted_data = extracted_data or {}
    
    # Default component weights summing to 1.0
    default_weights = {
        "interest_risk": 0.20,
        "fee_risk": 0.15,
        "penalty_risk": 0.20,
        "foreclosure_risk": 0.15,
        "variable_rate_risk": 0.10,
        "insurance_risk": 0.10,
        "complexity_risk": 0.10
    }
    w = weights if weights else default_weights

    # Base Scores (1.0 to 10.0) & Reasons
    components = {}

    # 1. Interest Risk
    rate = float(extracted_data.get("interest_rate", 10.5) or 10.5)
    if rate > 15.0:
        int_score, int_reason = 8.5, f"Interest rate of {rate}% p.a. is high relative to benchmark prime rates."
    elif rate > 12.0:
        int_score, int_reason = 6.5, f"Interest rate of {rate}% p.a. is moderately elevated."
    else:
        int_score, int_reason = 2.5, f"Competitive interest rate of {rate}% p.a."
    components["interest_risk"] = {"score": int_score, "explanation": int_reason}

    # 2. Fee Risk
    proc_fee = float(extracted_data.get("processing_fee", 2500) or 2500)
    loan_amt = float(extracted_data.get("loan_amount", 500000) or 500000)
    fee_pct = (proc_fee / loan_amt * 100) if loan_amt > 0 else 0.5
    if fee_pct > 2.5:
        fee_score, fee_reason = 8.0, f"Upfront processing fee of {fee_pct:.1f}% is significantly above standard 1% baseline."
    elif fee_pct > 1.0:
        fee_score, fee_reason = 5.5, f"Moderate processing fee of {fee_pct:.1f}%."
    else:
        fee_score, fee_reason = 2.0, f"Low upfront processing fee of {fee_pct:.1f}%."
    components["fee_risk"] = {"score": fee_score, "explanation": fee_reason}

    # 3. Penalty Risk
    has_penalty_clause = any(c.get("clause_type") == "Late Payment Penalty" for c in clauses)
    if has_penalty_clause:
        pen_score, pen_reason = 8.5, "High penal interest clause (compounded monthly) present for overdue payments."
    else:
        pen_score, pen_reason = 3.0, "Standard penalty terms detected."
    components["penalty_risk"] = {"score": pen_score, "explanation": pen_reason}

    # 4. Foreclosure Risk
    has_foreclosure_high = any(c.get("clause_type") == "Foreclosure Conditions" and c.get("risk_level") == "HIGH_RISK" for c in clauses)
    if has_foreclosure_high:
        fc_score, fc_reason = 8.0, "Restrictive foreclosure terms or high penalty charges on early repayment."
    else:
        fc_score, fc_reason = 3.5, "Moderate or standard prepayment terms."
    components["foreclosure_risk"] = {"score": fc_score, "explanation": fc_reason}

    # 5. Variable Rate Risk
    is_floating = extracted_data.get("interest_type") == "Floating" or any("Floating" in c.get("title", "") for c in clauses)
    if is_floating:
        vr_score, vr_reason = 7.0, "Floating interest rate creates payment volatility when benchmark rates increase."
    else:
        vr_score, vr_reason = 1.5, "Fixed interest rate eliminates variable rate exposure."
    components["variable_rate_risk"] = {"score": vr_score, "explanation": vr_reason}

    # 6. Insurance Risk
    has_insurance = any(c.get("clause_type") == "Insurance Requirement" for c in clauses)
    if has_insurance:
        ins_score, ins_reason = 6.5, "Mandatory credit shield insurance policy adds ancillary debt burden."
    else:
        ins_score, ins_reason = 2.0, "No mandatory insurance requirement detected."
    components["insurance_risk"] = {"score": ins_score, "explanation": ins_reason}

    # 7. Contract Complexity Risk
    high_count = sum(1 for c in clauses if c.get("risk_level") == "HIGH_RISK")
    if high_count >= 2:
        cx_score, cx_reason = 8.0, f"Contract contains {high_count} high-risk clauses requiring careful legal review."
    elif high_count == 1:
        cx_score, cx_reason = 5.0, "Contract contains 1 high-risk clause alongside standard terms."
    else:
        cx_score, cx_reason = 2.5, "Standard contract complexity with mostly low/medium risk conditions."
    components["complexity_risk"] = {"score": cx_score, "explanation": cx_reason}

    # Calculate Overall Weighted Score
    overall_score = round(sum(components[key]["score"] * w.get(key, 0.14) for key in components), 1)

    if overall_score >= 7.0:
        risk_level = "HIGH_RISK"
    elif overall_score >= 4.5:
        risk_level = "MEDIUM_RISK"
    else:
        risk_level = "LOW_RISK"

    # Assemble Evidence & Recommendations
    risk_factors = [components[k]["explanation"] for k in components if components[k]["score"] >= 5.5]
    evidence = [{
        "category": c["clause_type"],
        "snippet": c["text_snippet"],
        "risk_level": c["risk_level"]
    } for c in clauses]

    recommendations = []
    if is_floating:
        recommendations.append("Ensure your monthly budget can absorb a 1.5% to 2.0% potential spike in interest rates.")
    if has_foreclosure_high:
        recommendations.append("Negotiate a zero foreclosure fee clause if you intend to make early lump-sum repayments.")
    if has_penalty_clause:
        recommendations.append("Set up automated standing instructions 3 days prior to the due date to avoid steep penal charges.")
    if not recommendations:
        recommendations.append("The contract terms align with standard retail lending guidelines.")

    return {
        "overall_risk_score": overall_score,
        "risk_score": overall_score,
        "risk_level": risk_level,
        "risk_category": risk_level,
        "component_scores": components,
        "risk_factors": risk_factors,
        "evidence": evidence,
        "recommendations": recommendations,
        "why_explanation": f"Overall risk score of {overall_score}/10 derived from weighted components: " + ", ".join([f"{k.replace('_', ' ').title()}: {v['score']}" for k,v in components.items()])
    }


def _extract_matching_snippet(text: str, pattern: str) -> str:
    match = re.search(pattern, text)
    if match:
        snippet = match.group(0).strip()
        if len(snippet) > 160:
            snippet = snippet[:157] + "..."
        return snippet
    return "Clause snippet identified in contract text."
