import logging
from typing import Dict, Any, List
from services.rag_engine import query_rag_system, index_document

logger = logging.getLogger(__name__)

def evaluate_rag_pipeline(doc_id: str = "sample_eval_doc") -> Dict[str, Any]:
    """
    Evaluates RAG pipeline performance on a standardized evaluation dataset.
    Metrics evaluated:
    - Retrieval Relevance
    - Answer Correctness
    - Citation Correctness
    - Hallucination Rate
    - Unsupported Question Handling
    """
    sample_text = """
    LOAN AGREEMENT CONTRACT
    Section 1: Borrower & Lender Details
    Borrower: Rahul Sharma. Lender: HDFC Bank Ltd. Sanctioned Principal Amount: Rs. 500,000. Loan Tenure: 60 Months.
    
    Section 2: Interest & EMI Terms
    Annual Interest Rate: 10.5% per annum (Fixed Interest Rate). Monthly EMI: Rs. 10,747 payable on the 5th of every month.
    
    Section 3: Prepayment & Foreclosure
    Foreclosure charges of 3% on outstanding balance applicable if loan is closed within 24 months. No penalty after 24 months.
    
    Section 4: Penal Interest & Late Payment Fees
    Overdue EMI payments incur penal interest of 2% per month compounded monthly. Cheque bounce charge of Rs. 500.
    
    Section 5: Processing & Administrative Fees
    Upfront processing fee: Rs. 2,500 (0.5% of loan amount). Mandatory loan protector insurance premium: Rs. 4,000.
    """

    # Index evaluation sample doc
    index_document(
        doc_id=doc_id,
        filename="hdfc_eval_sample.pdf",
        text=sample_text,
        pages=[
            {"page_number": 1, "text": sample_text[:350]},
            {"page_number": 2, "text": sample_text[350:]}
        ]
    )

    eval_qa_pairs = [
        {
            "question": "What is the interest rate?",
            "expected_keywords": ["10.5%", "interest rate"],
            "expect_grounded": True,
            "type": "supported"
        },
        {
            "question": "What is the EMI?",
            "expected_keywords": ["10,747", "emi"],
            "expect_grounded": True,
            "type": "supported"
        },
        {
            "question": "What happens if payment is late?",
            "expected_keywords": ["2%", "penal", "late"],
            "expect_grounded": True,
            "type": "supported"
        },
        {
            "question": "Is foreclosure allowed?",
            "expected_keywords": ["foreclosure", "3%"],
            "expect_grounded": True,
            "type": "supported"
        },
        {
            "question": "What fees are charged?",
            "expected_keywords": ["processing fee", "2,500", "insurance"],
            "expect_grounded": True,
            "type": "supported"
        },
        {
            "question": "What is the loan tenure?",
            "expected_keywords": ["60", "months"],
            "expect_grounded": True,
            "type": "supported"
        },
        {
            "question": "What is the borrower's pet name and dog breed?",
            "expected_keywords": ["could not find enough information"],
            "expect_grounded": False,
            "type": "unsupported"
        }
    ]

    results = []
    correct_retrievals = 0
    correct_answers = 0
    correct_citations = 0
    hallucination_count = 0

    for qa in eval_qa_pairs:
        res = query_rag_system(qa["question"], doc_ids=[doc_id])
        ans = res["answer"].lower()
        sources = res.get("sources", [])

        is_grounded = res.get("grounded", False)
        
        # Check retrieval relevance
        if qa["type"] == "supported":
            has_rel = len(sources) > 0 and any("hdfc_eval_sample.pdf" in s.get("filename", "") for s in sources)
            if has_rel:
                correct_retrievals += 1

            # Check answer correctness
            has_kw = any(kw.lower() in ans for kw in qa["expected_keywords"])
            if has_kw:
                correct_answers += 1

            # Check citation correctness
            if sources and "page_number" in sources[0]:
                correct_citations += 1

            # Hallucination check
            if not is_grounded:
                hallucination_count += 1
        else:
            # Unsupported question test
            if "could not find enough information" in ans or not is_grounded:
                correct_answers += 1
                correct_retrievals += 1
                correct_citations += 1
            else:
                hallucination_count += 1

        results.append({
            "question": qa["question"],
            "answer": res["answer"],
            "confidence": res["confidence_score"],
            "sources_count": len(sources),
            "grounded": is_grounded,
            "passed": (qa["type"] == "supported" and len(sources) > 0) or (qa["type"] == "unsupported" and not is_grounded)
        })

    total_q = len(eval_qa_pairs)
    total_supported = sum(1 for q in eval_qa_pairs if q["type"] == "supported")

    retrieval_relevance = round((correct_retrievals / total_q) * 100, 1)
    answer_correctness = round((correct_answers / total_q) * 100, 1)
    citation_correctness = round((correct_citations / total_q) * 100, 1)
    hallucination_rate = round((hallucination_count / total_q) * 100, 1)

    return {
        "evaluation_summary": {
            "total_questions_tested": total_q,
            "supported_questions": total_supported,
            "unsupported_questions": total_q - total_supported,
            "retrieval_relevance_pct": retrieval_relevance,
            "answer_correctness_pct": answer_correctness,
            "citation_correctness_pct": citation_correctness,
            "hallucination_rate_pct": hallucination_rate
        },
        "test_results": results
    }
