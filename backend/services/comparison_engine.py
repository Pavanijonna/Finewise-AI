import uuid
import datetime
from typing import List, Dict, Any

def compare_loans(loans_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Multi-loan side-by-side comparison engine.
    Computes:
    - Effective Total Repayment + Fees
    - Risk rating
    - Composite Score ranking
    - Identifies: Best Overall, Lowest Cost, Lowest Risk
    - Explains rationale distinctly without single-metric bias.
    """
    if not loans_data:
        raise ValueError("No loan documents provided for comparison.")

    compared_items = []

    for item in loans_data:
        doc_id = item["doc_id"]
        filename = item["filename"]
        data = item.get("extracted_data", {})
        risk_data = item.get("risk_analysis", {})

        borrower_name = data.get("borrower_name", "Borrower")
        loan_amount = float(data.get("loan_amount", 500000.0) or 500000.0)
        interest_rate = float(data.get("interest_rate", 10.5) or 10.5)
        interest_type = data.get("interest_type", "Fixed")
        tenure_months = int(data.get("tenure", 60) or 60)
        emi = float(data.get("emi", 0.0) or 0.0)
        processing_fee = float(data.get("processing_fee", 2500.0) or 2500.0)
        total_interest = float(data.get("total_interest", 0.0) or 0.0)
        total_repayment = float(data.get("total_repayment", 0.0) or 0.0)
        foreclosure_charges = data.get("foreclosure_charges", "Standard")
        late_penalty = data.get("late_payment_penalties", "Standard")
        risk_score = float(risk_data.get("overall_risk_score", risk_data.get("risk_score", 5.0)) or 5.0)

        effective_total_cost = total_repayment + processing_fee

        pros = []
        cons = []

        if interest_rate <= 9.5:
            pros.append("Competitive low interest rate.")
        elif interest_rate >= 12.0:
            cons.append("Higher interest rate relative to market standard.")

        if interest_type == "Fixed":
            pros.append("Fixed EMI guarantees predictable monthly payments.")
        else:
            cons.append("Floating rate creates interest rate volatility risk.")

        if processing_fee <= 1500:
            pros.append("Low upfront administrative processing charges.")
        elif processing_fee >= 5000:
            cons.append("Significant upfront processing fee.")

        if "zero" in foreclosure_charges.lower() or "nil" in foreclosure_charges.lower() or "no" in foreclosure_charges.lower():
            pros.append("Zero foreclosure penalty charges for early repayment.")
        else:
            cons.append(f"Foreclosure penalty applicable: {foreclosure_charges}")

        if risk_score <= 4.0:
            pros.append("Favorable contract clauses with low borrower risk.")
        elif risk_score >= 7.0:
            cons.append(f"High contractual risk rating ({risk_score}/10).")

        compared_items.append({
            "doc_id": doc_id,
            "filename": filename,
            "borrower_name": borrower_name,
            "loan_amount": loan_amount,
            "interest_rate": interest_rate,
            "interest_type": interest_type,
            "tenure_months": tenure_months,
            "emi": emi,
            "processing_fee": processing_fee,
            "total_interest": total_interest,
            "total_repayment": total_repayment,
            "effective_total_cost": effective_total_cost,
            "foreclosure_charges": foreclosure_charges,
            "late_penalty": late_penalty,
            "risk_score": risk_score,
            "pros": pros,
            "cons": cons
        })

    # Sort loans to find Lowest Cost and Lowest Risk options
    sorted_by_cost = sorted(compared_items, key=lambda x: x["effective_total_cost"])
    sorted_by_risk = sorted(compared_items, key=lambda x: x["risk_score"])

    # Composite Ranking (Cost Weight 60%, Risk Weight 40%)
    min_cost = sorted_by_cost[0]["effective_total_cost"] if sorted_by_cost else 1.0
    for item in compared_items:
        cost_ratio = item["effective_total_cost"] / min_cost if min_cost > 0 else 1.0
        composite_rank_score = (cost_ratio * 0.6) + ((item["risk_score"] / 10.0) * 0.4)
        item["composite_score"] = round(composite_rank_score, 3)

    ranked_items = sorted(compared_items, key=lambda x: x["composite_score"])
    for idx, item in enumerate(ranked_items):
        item["overall_rank"] = idx + 1

    best_option = ranked_items[0]
    lowest_cost_option = sorted_by_cost[0]
    lowest_risk_option = sorted_by_risk[0]

    reasoning = (
        f"Loan '{best_option['filename']}' is ranked as the overall best choice. "
        f"It balances total cost (INR {best_option['effective_total_cost']:,.2f}) with contract risk score ({best_option['risk_score']}/10.0). "
        f"Note: Loan '{lowest_cost_option['filename']}' offers the lowest raw repayment cost (INR {lowest_cost_option['effective_total_cost']:,.2f}), "
        f"while Loan '{lowest_risk_option['filename']}' offers the lowest contractual risk score ({lowest_risk_option['risk_score']}/10.0)."
    )

    return {
        "comparison_id": f"comp_{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.datetime.utcnow(),
        "compared_loans": ranked_items,
        "best_option_doc_id": best_option["doc_id"],
        "best_option_name": best_option["filename"],
        "recommendation_reasoning": reasoning,
        "lowest_cost_doc_id": lowest_cost_option["doc_id"],
        "lowest_risk_doc_id": lowest_risk_option["doc_id"]
    }
