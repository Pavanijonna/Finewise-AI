import sys
import os
from fastapi.testclient import TestClient

# Add backend directory to python path
sys.path.append(os.path.dirname(__file__))

from main import app

def test_full_pipeline():
    client = TestClient(app)
    
    print("--- 1. Testing Root Endpoint ---")
    res = client.get("/")
    assert res.status_code == 200
    print("Root response:", res.json())

    print("\n--- 2. Loading Sample Documents ---")
    res = client.post("/api/load-samples")
    assert res.status_code == 200
    data = res.json()
    print("Samples loaded:", data)

    print("\n--- 3. Fetching All Documents ---")
    res = client.get("/api/documents")
    assert res.status_code == 200
    docs = res.json()
    print(f"Retrieved {len(docs)} documents.")
    assert len(docs) >= 3

    first_doc_id = docs[0]["id"]
    print(f"\n--- 4. Fetching Document Details for {first_doc_id} ---")
    res = client.get(f"/api/documents/{first_doc_id}")
    assert res.status_code == 200
    detail = res.json()
    print("Document Extracted Data:", detail["extracted_data"])
    print("Clauses Flagged:", len(detail["clauses"]))
    print("Risk Analysis:", detail["risk_analysis"])

    print(f"\n--- 5. Financial Calculations for {first_doc_id} ---")
    res = client.get(f"/api/calculate/{first_doc_id}")
    assert res.status_code == 200
    calc = res.json()
    print(f"Calculated EMI: Rs.{calc['calculated_emi']}, Total Repayment: Rs.{calc['total_repayment_amount']}")

    print("\n--- 6. Multi-Loan Comparison ---")
    doc_ids = [d["id"] for d in docs]
    res = client.post("/api/compare", json={"doc_ids": doc_ids})
    assert res.status_code == 200
    comp = res.json()
    print("Best Loan Option:", comp["best_option_name"])
    print("Recommendation Rationale:", comp["recommendation_reasoning"])

    print("\n--- 7. RAG Assistant Query ---")
    res = client.post("/api/chat", json={"query": "Is this loan risky?", "doc_ids": [first_doc_id]})
    assert res.status_code == 200
    chat_res = res.json()
    print("Sources Found:", len(chat_res["sources"]))

    print("\n--- 8. PDF Report Generation ---")
    res = client.get(f"/api/report/{first_doc_id}/pdf")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    print(f"PDF Report generated successfully ({len(res.content)} bytes).")

    print("\nALL BACKEND VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_full_pipeline()
