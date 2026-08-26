import sys
import os
from fastapi.testclient import TestClient

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from main import app
from services.financial_calculator import calculate_loan_financials
from services.financial_validator import validate_financial_consistency
from services.clause_detector import analyze_clauses, compute_component_risk_scores
from services.ml_engine import train_and_evaluate_ml_models, predict_contract_risk
from services.rag_evaluator import evaluate_rag_pipeline

client = TestClient(app)

# 1. Financial Math Unit Tests
def test_financial_calculator_math():
    print("[TEST 1/6] Testing Financial Calculator Formulas...")
    res = calculate_loan_financials(
        loan_amount=500000.0,
        annual_interest_rate=10.5,
        tenure_months=60,
        processing_fee=2500.0
    )
    assert res["calculated_emi"] > 0
    assert abs(res["calculated_emi"] - 10747.0) < 50.0  # Approx 10,747
    assert res["total_repayment_amount"] > 500000.0
    assert len(res["amortization_schedule"]) == 60
    assert res["effective_apr"] > 10.5  # APR includes fee
    print("  [OK] Financial Calculator test passed.")


def test_zero_interest_calculator():
    res = calculate_loan_financials(
        loan_amount=120000.0,
        annual_interest_rate=0.0,
        tenure_months=12,
        processing_fee=0.0
    )
    assert res["calculated_emi"] == 10000.0
    assert res["total_interest_payable"] == 0.0
    assert res["total_repayment_amount"] == 120000.0
    print("  [OK] Zero interest calculator test passed.")


# 2. Financial Validation Engine Tests
def test_financial_consistency_validator():
    print("[TEST 2/6] Testing Financial Consistency Validator...")
    # Valid loan
    val_good = validate_financial_consistency(
        loan_amount=500000.0,
        interest_rate=10.5,
        tenure_months=60,
        emi=10747.0,
        total_interest=144820.0,
        total_repayment=644820.0
    )
    assert val_good["validation_status"] == "VERIFIED"
    assert val_good["is_valid"] is True

    # Conflicting / Inconsistent EMI
    val_bad = validate_financial_consistency(
        loan_amount=500000.0,
        interest_rate=10.5,
        tenure_months=60,
        emi=2000.0,  # Far too low
        total_interest=144820.0,
        total_repayment=644820.0
    )
    assert val_bad["validation_status"] == "VERIFICATION_REQUIRED"
    assert len(val_bad["issues"]) > 0
    print("  [OK] Financial consistency validator test passed.")


# 3. 7-Component Risk Scoring Tests
def test_7_component_risk_scoring():
    print("[TEST 3/6] Testing 7-Component Risk Scoring Engine...")
    sample_text = "This agreement has a floating interest rate. Foreclosure penalty of 4% applies. Penal interest of 2% per month on late payments."
    clauses = analyze_clauses(sample_text)
    assert len(clauses) > 0

    risk_data = compute_component_risk_scores(clauses, {"loan_amount": 500000, "interest_rate": 14.0, "processing_fee": 15000})
    assert "component_scores" in risk_data
    assert len(risk_data["component_scores"]) == 7
    assert "interest_risk" in risk_data["component_scores"]
    assert "why_explanation" in risk_data
    print("  [OK] 7-Component Risk scoring test passed.")


# 4. Machine Learning & Threshold Tuning Tests
def test_ml_pipeline_and_threshold_tuning():
    print("[TEST 4/6] Testing ML Models & Threshold Optimization Pipeline...")
    eval_res = train_and_evaluate_ml_models(selected_threshold=0.40)
    assert "models" in eval_res
    assert "Logistic Regression" in eval_res["models"]
    assert "Random Forest" in eval_res["models"]
    assert "XGBoost" in eval_res["models"]

    rf_metrics = eval_res["models"]["Random Forest"]
    assert "precision" in rf_metrics
    assert "recall" in rf_metrics
    assert "f1" in rf_metrics
    assert "roc_auc" in rf_metrics
    assert "confusion_matrix" in rf_metrics
    assert len(rf_metrics["threshold_sweep"]) >= 8

    # Test Single Contract Prediction
    pred = predict_contract_risk(
        contract_features={
            "dti": 0.45,
            "interest_rate": 16.0,
            "processing_fee_pct": 3.0,
            "penal_rate": 30.0,
            "credit_score_norm": 0.50,
            "has_foreclosure_penalty": True,
            "is_floating_rate": True,
            "has_mandatory_insurance": True
        },
        threshold=0.40
    )
    assert "risk_probability" in pred
    assert "explainable_statement" in pred
    assert len(pred["positive_risk_factors"]) > 0
    print("  [OK] ML training, threshold tuning & explainable prediction test passed.")


# 5. RAG Evaluation Benchmark Test
def test_rag_eval_pipeline():
    print("[TEST 5/6] Testing RAG System & Grounded Evaluator...")
    eval_res = evaluate_rag_pipeline()
    assert "evaluation_summary" in eval_res
    summary = eval_res["evaluation_summary"]
    assert summary["total_questions_tested"] == 7
    assert summary["retrieval_relevance_pct"] >= 70.0
    assert summary["answer_correctness_pct"] >= 70.0
    assert summary["hallucination_rate_pct"] <= 30.0
    print(f"  [OK] RAG Evaluation passed: Accuracy={summary['answer_correctness_pct']}%, Relevance={summary['retrieval_relevance_pct']}%.")


# 6. API Integration Tests
def test_api_full_flow():
    print("[TEST 6/6] Testing End-to-End FastAPI Endpoints...")
    # Health endpoint
    h = client.get("/api/health")
    assert h.status_code == 200
    assert h.json()["status"] == "online"

    # Sample doc loading
    s = client.post("/api/load-samples")
    assert s.status_code == 200

    # Get documents
    docs_res = client.get("/api/documents")
    assert docs_res.status_code == 200
    docs = docs_res.json()
    assert len(docs) >= 3

    first_id = docs[0]["id"]

    # Get doc details
    d_res = client.get(f"/api/documents/{first_id}")
    assert d_res.status_code == 200
    det = d_res.json()
    assert "extracted_data" in det
    assert "risk_analysis" in det

    # Calculations
    c_res = client.get(f"/api/calculate/{first_id}")
    assert c_res.status_code == 200

    # Multi-loan comparison
    comp_res = client.post("/api/compare", json={"doc_ids": [d["id"] for d in docs]})
    assert comp_res.status_code == 200
    assert "best_option_name" in comp_res.json()

    # RAG Chat
    chat_res = client.post("/api/chat", json={"query": "What is the interest rate?", "doc_ids": [first_id]})
    assert chat_res.status_code == 200
    assert len(chat_res.json()["sources"]) > 0

    # ML Evaluation endpoint
    ml_res = client.get("/api/ml/evaluation?threshold=0.50")
    assert ml_res.status_code == 200

    # PDF Report export
    pdf_res = client.get(f"/api/report/{first_id}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"

    print("  [OK] Full API integration flow test passed.")


def run_all_tests():
    print("==================================================")
    print("      RUNNING FINWISE AI BACKEND TEST SUITE       ")
    print("==================================================")
    test_financial_calculator_math()
    test_zero_interest_calculator()
    test_financial_consistency_validator()
    test_7_component_risk_scoring()
    test_ml_pipeline_and_threshold_tuning()
    test_rag_eval_pipeline()
    test_api_full_flow()
    print("==================================================")
    print("   ALL BACKEND UNIT & INTEGRATION TESTS PASSED!   ")
    print("==================================================")

if __name__ == "__main__":
    run_all_tests()
