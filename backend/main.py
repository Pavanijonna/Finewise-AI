import os
import uuid
import time
import logging
from typing import List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session

from database import engine, get_db, Base
import models
import schemas
from services.ocr_service import extract_text_from_file
from services.nlp_extractor import extract_financial_data
from services.financial_validator import validate_financial_consistency
from services.financial_calculator import calculate_loan_financials
from services.clause_detector import analyze_clauses, compute_component_risk_scores
from services.comparison_engine import compare_loans
from services.rag_engine import index_document, query_rag_system
from services.rag_evaluator import evaluate_rag_pipeline
from services.report_generator import generate_pdf_report
from services.ml_engine import train_and_evaluate_ml_models, predict_contract_risk

# Initialize Database tables
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("finwise-backend")

app = FastAPI(
    title="FinWise AI — Intelligent Financial Decision Support System",
    description="Full-Stack Decision Support API powered by OCR, NLP, RAG, Financial Math, and Explainable Machine Learning.",
    version="2.0.0"
)

# Middleware for structured request logging with timing and request_id
@app.middleware("http")
async def log_requests(request: Request, call_next):
    req_id = f"req_{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    logger.info(f"[{req_id}] Start {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Process-Time-MS"] = f"{process_time:.2f}"
        logger.info(f"[{req_id}] Completed {request.method} {request.url.path} with status {response.status_code} in {process_time:.2f}ms")
        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(f"[{req_id}] Failed {request.method} {request.url.path}: {str(e)} in {process_time:.2f}ms")
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred.", "request_id": req_id, "error": str(e)}
        )

# CORS Middleware setup
raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
if raw_origins.strip() == "*":
    origins = ["*"]
else:
    origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "system": "FinWise AI - Intelligent Financial Decision Support System",
        "version": "2.0.0",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }


@app.post("/api/upload", response_model=List[schemas.DocumentResponse])
@app.post("/api/documents/upload", response_model=List[schemas.DocumentResponse])
async def upload_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Validates, ingests, performs OCR, NLP extraction, financial validation,
    7-component risk scoring, and indexes documents into RAG engine.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for upload.")

    uploaded_docs = []
    allowed_extensions = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}

    for file in files:
        file_ext = os.path.splitext(file.filename)[1].lower()
        if not file_ext:
            file_ext = ".pdf"

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type '{file.filename}'. Allowed formats: PDF, PNG, JPG, TXT."
            )

        doc_id = f"doc_{uuid.uuid4().hex[:10]}"
        saved_path = os.path.join(UPLOAD_DIR, f"{doc_id}{file_ext}")

        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail=f"File '{file.filename}' is empty (0 bytes).")
        if len(content) > 15 * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File '{file.filename}' exceeds 15MB size limit.")

        with open(saved_path, "wb") as f:
            f.write(content)

        # 1. OCR & Document Processing
        try:
            ocr_res = extract_text_from_file(saved_path)
        except Exception as e:
            logger.error(f"OCR failure on file {file.filename}: {e}")
            raise HTTPException(status_code=422, detail=f"Failed to perform OCR on '{file.filename}': {str(e)}")

        text_content = ocr_res["text_content"]
        ocr_conf = ocr_res["ocr_confidence"]
        ocr_warn = ocr_res["ocr_warning"]
        pages = ocr_res["pages"]

        doc_record = models.Document(
            id=doc_id,
            filename=file.filename,
            file_path=saved_path,
            file_type=file_ext.replace(".", "").upper(),
            status="PROCESSED" if text_content else "UPLOADED",
            text_content=text_content,
            ocr_confidence=ocr_conf,
            ocr_warning=ocr_warn,
            page_count=len(pages)
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)

        # 2. Hybrid Entity Extraction
        extracted = extract_financial_data(text_content, file.filename, pages=pages)
        
        # 3. Financial Consistency Validation
        val_res = validate_financial_consistency(
            loan_amount=extracted.get("loan_amount", 0.0),
            interest_rate=extracted.get("interest_rate", 0.0),
            tenure_months=extracted.get("tenure", 0),
            emi=extracted.get("emi", 0.0),
            total_interest=extracted.get("total_interest", 0.0),
            total_repayment=extracted.get("total_repayment", 0.0),
            processing_fee=extracted.get("processing_fee", 0.0)
        )

        ext_record = models.ExtractedData(
            doc_id=doc_id,
            borrower_name=extracted.get("borrower_name"),
            lender_name=extracted.get("lender_name"),
            loan_type=extracted.get("loan_type"),
            loan_amount=extracted.get("loan_amount"),
            interest_rate=extracted.get("interest_rate"),
            interest_type=extracted.get("interest_type"),
            tenure_months=extracted.get("tenure"),
            emi=extracted.get("emi"),
            processing_fee=extracted.get("processing_fee"),
            processing_fee_pct=extracted.get("processing_fee_pct"),
            insurance_fee=extracted.get("insurance_fee"),
            total_interest=extracted.get("total_interest"),
            total_repayment=extracted.get("total_repayment"),
            foreclosure_charges=extracted.get("foreclosure_charges"),
            late_penalty=extracted.get("late_payment_fee"),
            due_dates=extracted.get("due_date"),
            collateral=extracted.get("collateral"),
            validation_status=val_res["validation_status"],
            validation_issues=val_res["issues"],
            raw_json=extracted.get("_structured", extracted)
        )
        db.add(ext_record)

        # 4. Clause Detection & 7-Component Risk Analysis
        clauses_list = analyze_clauses(text_content)
        for c in clauses_list:
            clause_record = models.Clause(
                doc_id=doc_id,
                title=c["title"],
                clause_type=c["clause_type"],
                text_snippet=c["text_snippet"],
                risk_level=c["risk_level"],
                simple_explanation=c["simple_explanation"],
                impact_score=c.get("impact_score", 5.0)
            )
            db.add(clause_record)

        db.commit()

        # Risk Analysis Record
        risk_comp_data = compute_component_risk_scores(clauses_list, extracted)
        risk_record = models.RiskAnalysisRecord(
            doc_id=doc_id,
            overall_risk_score=risk_comp_data["overall_risk_score"],
            risk_level=risk_comp_data["risk_level"],
            component_scores=risk_comp_data["component_scores"],
            risk_factors=risk_comp_data["risk_factors"],
            evidence=risk_comp_data["evidence"],
            recommendations=risk_comp_data["recommendations"]
        )
        db.add(risk_record)
        db.commit()

        # 5. RAG Engine Indexing with Page Numbers & Section Metadata
        index_document(doc_id, file.filename, text_content, pages=pages)

        uploaded_docs.append(doc_record)

    return [
        schemas.DocumentResponse(
            id=d.id,
            filename=d.filename,
            file_type=d.file_type,
            upload_time=d.upload_time,
            status=d.status,
            ocr_confidence=d.ocr_confidence,
            ocr_warning=d.ocr_warning,
            text_snippet=d.text_content[:200] if d.text_content else ""
        ) for d in uploaded_docs
    ]


@app.get("/api/documents", response_model=List[schemas.DocumentResponse])
def get_all_documents(db: Session = Depends(get_db)):
    docs = db.query(models.Document).order_by(models.Document.upload_time.desc()).all()
    return [
        schemas.DocumentResponse(
            id=d.id,
            filename=d.filename,
            file_type=d.file_type,
            upload_time=d.upload_time,
            status=d.status,
            ocr_confidence=d.ocr_confidence,
            ocr_warning=d.ocr_warning,
            text_snippet=d.text_content[:200] if d.text_content else ""
        ) for d in docs
    ]


@app.get("/api/documents/{doc_id}")
def get_document_details(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document with ID '{doc_id}' not found.")

    ext = db.query(models.ExtractedData).filter(models.ExtractedData.doc_id == doc_id).first()
    clauses = db.query(models.Clause).filter(models.Clause.doc_id == doc_id).all()
    risk_rec = db.query(models.RiskAnalysisRecord).filter(models.RiskAnalysisRecord.doc_id == doc_id).first()

    clauses_dicts = [{
        "id": c.id,
        "title": c.title,
        "clause_type": c.clause_type,
        "text_snippet": c.text_snippet,
        "risk_level": c.risk_level,
        "simple_explanation": c.simple_explanation,
        "impact_score": c.impact_score,
        "page_number": c.page_number
    } for c in clauses]

    ext_data_dict = {
        "borrower_name": ext.borrower_name if ext else "Valued Borrower",
        "lender_name": ext.lender_name if ext else "Financial Institution",
        "loan_type": ext.loan_type if ext else "Personal Loan",
        "loan_amount": ext.loan_amount if ext else 0.0,
        "interest_rate": ext.interest_rate if ext else 0.0,
        "interest_type": ext.interest_type if ext else "Fixed",
        "tenure": ext.tenure_months if ext else 0,
        "emi": ext.emi if ext else 0.0,
        "processing_fee": ext.processing_fee if ext else 0.0,
        "processing_fee_pct": ext.processing_fee_pct if ext else 0.0,
        "insurance_fee": ext.insurance_fee if ext else 0.0,
        "total_interest": ext.total_interest if ext else 0.0,
        "total_repayment": ext.total_repayment if ext else 0.0,
        "foreclosure_charges": ext.foreclosure_charges if ext else "Standard",
        "late_payment_penalties": ext.late_penalty if ext else "Standard",
        "due_dates": ext.due_dates if ext else "5th of every month",
        "collateral": ext.collateral if ext else "Unsecured",
        "validation_status": ext.validation_status if ext else "VERIFIED",
        "validation_issues": ext.validation_issues if ext else [],
        "structured_entities": ext.raw_json if ext else {}
    }

    if risk_rec:
        risk_info = {
            "overall_risk_score": risk_rec.overall_risk_score,
            "risk_score": risk_rec.overall_risk_score,
            "risk_level": risk_rec.risk_level,
            "risk_category": risk_rec.risk_level,
            "component_scores": risk_rec.component_scores,
            "risk_factors": risk_rec.risk_factors,
            "evidence": risk_rec.evidence,
            "recommendations": risk_rec.recommendations,
            "why_explanation": f"Evaluated 7 risk components for document '{doc.filename}'."
        }
    else:
        risk_info = compute_component_risk_scores(clauses_dicts, ext_data_dict)

    return {
        "doc_id": doc.id,
        "filename": doc.filename,
        "upload_time": doc.upload_time,
        "status": doc.status,
        "ocr_confidence": doc.ocr_confidence,
        "ocr_warning": doc.ocr_warning,
        "page_count": doc.page_count,
        "extracted_data": ext_data_dict,
        "clauses": clauses_dicts,
        "risk_analysis": risk_info,
        "text_content": doc.text_content
    }


@app.post("/api/documents/{doc_id}/analyze")
def reanalyze_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    text = doc.text_content or ""
    extracted = extract_financial_data(text, doc.filename)
    val_res = validate_financial_consistency(
        loan_amount=extracted.get("loan_amount", 0.0),
        interest_rate=extracted.get("interest_rate", 0.0),
        tenure_months=extracted.get("tenure", 0),
        emi=extracted.get("emi", 0.0),
        total_interest=extracted.get("total_interest", 0.0),
        total_repayment=extracted.get("total_repayment", 0.0),
        processing_fee=extracted.get("processing_fee", 0.0)
    )

    clauses_list = analyze_clauses(text)
    risk_comp_data = compute_component_risk_scores(clauses_list, extracted)

    return {
        "doc_id": doc_id,
        "status": "REANALYZED",
        "extracted_data": extracted,
        "validation": val_res,
        "clauses_count": len(clauses_list),
        "risk_analysis": risk_comp_data
    }


@app.get("/api/documents/{doc_id}/risk")
@app.get("/api/risk/{doc_id}")
def get_doc_risk_details(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    ext = db.query(models.ExtractedData).filter(models.ExtractedData.doc_id == doc_id).first()
    clauses = db.query(models.Clause).filter(models.Clause.doc_id == doc_id).all()
    clauses_dicts = [{
        "title": c.title,
        "clause_type": c.clause_type,
        "text_snippet": c.text_snippet,
        "risk_level": c.risk_level,
        "simple_explanation": c.simple_explanation
    } for c in clauses]

    ext_dict = {"loan_amount": ext.loan_amount, "interest_rate": ext.interest_rate, "processing_fee": ext.processing_fee, "interest_type": ext.interest_type} if ext else {}
    risk_info = compute_component_risk_scores(clauses_dicts, ext_dict)

    return {
        "doc_id": doc_id,
        "filename": doc.filename,
        "risk_analysis": risk_info
    }


@app.get("/api/calculate/{doc_id}", response_model=schemas.FinancialCalculationResponse)
def calculate_doc_financials(doc_id: str, db: Session = Depends(get_db)):
    ext = db.query(models.ExtractedData).filter(models.ExtractedData.doc_id == doc_id).first()
    if not ext:
        raise HTTPException(status_code=404, detail="Extracted data for document not found.")

    result = calculate_loan_financials(
        loan_amount=ext.loan_amount or 500000.0,
        annual_interest_rate=ext.interest_rate or 10.5,
        tenure_months=ext.tenure_months or 60,
        processing_fee=ext.processing_fee or 2500.0,
        emi_override=ext.emi or 0.0
    )

    return schemas.FinancialCalculationResponse(
        doc_id=doc_id,
        loan_amount=result["loan_amount"],
        annual_interest_rate=result["annual_interest_rate"],
        tenure_months=result["tenure_months"],
        calculated_emi=result["calculated_emi"],
        total_interest_payable=result["total_interest_payable"],
        total_repayment_amount=result["total_repayment_amount"],
        processing_fee=result["processing_fee"],
        processing_fee_percentage=result["processing_fee_percentage"],
        effective_apr=result["effective_apr"],
        amortization_schedule=result["amortization_schedule"]
    )


@app.post("/api/compare", response_model=schemas.ComparisonResponse)
@app.post("/api/loans/compare", response_model=schemas.ComparisonResponse)
def compare_loan_documents(req: schemas.ComparisonRequest, db: Session = Depends(get_db)):
    doc_ids = req.doc_ids
    if not doc_ids:
        docs = db.query(models.Document).all()
        doc_ids = [d.id for d in docs]

    if not doc_ids:
        raise HTTPException(status_code=400, detail="No documents available for multi-loan comparison.")

    loans_data = []
    for d_id in doc_ids:
        doc = db.query(models.Document).filter(models.Document.id == d_id).first()
        ext = db.query(models.ExtractedData).filter(models.ExtractedData.doc_id == d_id).first()
        clauses = db.query(models.Clause).filter(models.Clause.doc_id == d_id).all()
        clauses_dicts = [{
            "title": c.title,
            "clause_type": c.clause_type,
            "text_snippet": c.text_snippet,
            "risk_level": c.risk_level,
            "simple_explanation": c.simple_explanation
        } for c in clauses]

        ext_dict = {
            "borrower_name": ext.borrower_name,
            "loan_amount": ext.loan_amount,
            "interest_rate": ext.interest_rate,
            "interest_type": ext.interest_type,
            "tenure": ext.tenure_months,
            "emi": ext.emi,
            "processing_fee": ext.processing_fee,
            "total_interest": ext.total_interest,
            "total_repayment": ext.total_repayment,
            "foreclosure_charges": ext.foreclosure_charges,
            "late_payment_penalties": ext.late_penalty
        } if ext else {}

        risk_info = compute_component_risk_scores(clauses_dicts, ext_dict)

        if doc and ext:
            loans_data.append({
                "doc_id": doc.id,
                "filename": doc.filename,
                "extracted_data": ext_dict,
                "risk_analysis": risk_info
            })

    if not loans_data:
        raise HTTPException(status_code=404, detail="No extracted loan data found for comparison.")

    return compare_loans(loans_data)


@app.post("/api/chat", response_model=schemas.ChatResponse)
@app.post("/api/documents/{doc_id}/chat", response_model=schemas.ChatResponse)
def rag_chat(req: schemas.ChatRequest, doc_id: Optional[str] = None):
    target_docs = req.doc_ids
    if doc_id:
        target_docs = [doc_id]

    res = query_rag_system(query=req.query, doc_ids=target_docs)
    return schemas.ChatResponse(
        answer=res["answer"],
        sources=res.get("sources", []),
        confidence_score=res.get("confidence_score", 0.0),
        grounded=res.get("grounded", True),
        disclaimer=res.get("disclaimer")
    )


@app.get("/api/report/{doc_id}/pdf")
@app.get("/api/reports/{doc_id}")
def export_pdf_report(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    ext = db.query(models.ExtractedData).filter(models.ExtractedData.doc_id == doc_id).first()
    clauses = db.query(models.Clause).filter(models.Clause.doc_id == doc_id).all()

    if not doc or not ext:
        raise HTTPException(status_code=404, detail="Document details not found.")

    clauses_dicts = [{
        "title": c.title,
        "clause_type": c.clause_type,
        "text_snippet": c.text_snippet,
        "risk_level": c.risk_level,
        "simple_explanation": c.simple_explanation
    } for c in clauses]

    ext_dict = {
        "borrower_name": ext.borrower_name,
        "lender_name": ext.lender_name,
        "loan_type": ext.loan_type,
        "loan_amount": ext.loan_amount,
        "interest_rate": ext.interest_rate,
        "interest_type": ext.interest_type,
        "tenure": ext.tenure_months,
        "emi": ext.emi,
        "processing_fee": ext.processing_fee,
        "total_interest": ext.total_interest,
        "total_repayment": ext.total_repayment
    }

    risk_info = compute_component_risk_scores(clauses_dicts, ext_dict)

    doc_data = {
        "doc_id": doc.id,
        "filename": doc.filename,
        **ext_dict
    }

    pdf_bytes = generate_pdf_report(doc_data, clauses_dicts, risk_info)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=FinWise_Report_{doc_id}.pdf"}
    )


@app.get("/api/ml/evaluation")
def get_ml_evaluation_metrics(threshold: float = 0.50):
    """
    Developer/Admin endpoint returning ML model evaluation metrics across
    Logistic Regression, Random Forest, and XGBoost with threshold tuning & confusion matrix.
    """
    return train_and_evaluate_ml_models(selected_threshold=threshold)


@app.post("/api/ml/predict", response_model=schemas.MLPredictResponse)
def predict_risk_ml(req: schemas.MLPredictRequest):
    features = {
        "dti": req.dti,
        "interest_rate": req.interest_rate,
        "processing_fee_pct": req.processing_fee_pct,
        "penal_rate": req.penal_rate,
        "credit_score_norm": req.credit_score_norm,
        "has_foreclosure_penalty": req.has_foreclosure_penalty,
        "is_floating_rate": req.is_floating_rate,
        "has_mandatory_insurance": req.has_mandatory_insurance
    }
    return predict_contract_risk(features, model_name=req.model_name, threshold=req.decision_threshold)


@app.post("/api/rag/eval")
def run_rag_eval_suite():
    return evaluate_rag_pipeline()


@app.post("/api/load-samples")
def load_sample_documents(db: Session = Depends(get_db)):
    """
    Populates sample loan contracts (HDFC Personal Loan, SBI Home Loan, Axis Car Loan) for instant demo testing.
    """
    sample_dir = os.path.join(os.path.dirname(__file__), "sample_docs")
    sample_files = ["hdfc_personal_loan.pdf", "sbi_home_loan.pdf", "axis_car_loan.pdf"]

    created_docs = []
    for s_file in sample_files:
        s_path = os.path.join(sample_dir, s_file)
        if not os.path.exists(s_path):
            continue

        doc_id = f"sample_{s_file.replace('.pdf', '')}"
        
        # Ingest & Process
        ocr_res = extract_text_from_file(s_path)
        text_content = ocr_res["text_content"]
        pages = ocr_res["pages"]

        existing = db.query(models.Document).filter(models.Document.id == doc_id).first()
        if existing:
            index_document(doc_id, s_file, existing.text_content or text_content, pages=pages)
            created_docs.append(existing.id)
            continue

        doc_record = models.Document(
            id=doc_id,
            filename=s_file,
            file_path=s_path,
            file_type="PDF",
            status="PROCESSED",
            text_content=text_content,
            ocr_confidence=ocr_res["ocr_confidence"],
            ocr_warning=ocr_res["ocr_warning"],
            page_count=len(pages)
        )
        db.add(doc_record)
        db.commit()

        extracted = extract_financial_data(text_content, s_file, pages=pages)
        val_res = validate_financial_consistency(
            loan_amount=extracted.get("loan_amount", 0.0),
            interest_rate=extracted.get("interest_rate", 0.0),
            tenure_months=extracted.get("tenure", 0),
            emi=extracted.get("emi", 0.0),
            total_interest=extracted.get("total_interest", 0.0),
            total_repayment=extracted.get("total_repayment", 0.0),
            processing_fee=extracted.get("processing_fee", 0.0)
        )

        ext_record = models.ExtractedData(
            doc_id=doc_id,
            borrower_name=extracted.get("borrower_name"),
            lender_name=extracted.get("lender_name"),
            loan_type=extracted.get("loan_type"),
            loan_amount=extracted.get("loan_amount"),
            interest_rate=extracted.get("interest_rate"),
            interest_type=extracted.get("interest_type"),
            tenure_months=extracted.get("tenure"),
            emi=extracted.get("emi"),
            processing_fee=extracted.get("processing_fee"),
            processing_fee_pct=extracted.get("processing_fee_pct"),
            insurance_fee=extracted.get("insurance_fee"),
            total_interest=extracted.get("total_interest"),
            total_repayment=extracted.get("total_repayment"),
            foreclosure_charges=extracted.get("foreclosure_charges"),
            late_penalty=extracted.get("late_payment_fee"),
            due_dates=extracted.get("due_date"),
            collateral=extracted.get("collateral"),
            validation_status=val_res["validation_status"],
            validation_issues=val_res["issues"],
            raw_json=extracted.get("_structured", extracted)
        )
        db.add(ext_record)

        clauses_list = analyze_clauses(text_content)
        for c in clauses_list:
            clause_record = models.Clause(
                doc_id=doc_id,
                title=c["title"],
                clause_type=c["clause_type"],
                text_snippet=c["text_snippet"],
                risk_level=c["risk_level"],
                simple_explanation=c["simple_explanation"],
                impact_score=c.get("impact_score", 5.0)
            )
            db.add(clause_record)

        db.commit()

        risk_comp_data = compute_component_risk_scores(clauses_list, extracted)
        risk_record = models.RiskAnalysisRecord(
            doc_id=doc_id,
            overall_risk_score=risk_comp_data["overall_risk_score"],
            risk_level=risk_comp_data["risk_level"],
            component_scores=risk_comp_data["component_scores"],
            risk_factors=risk_comp_data["risk_factors"],
            evidence=risk_comp_data["evidence"],
            recommendations=risk_comp_data["recommendations"]
        )
        db.add(risk_record)
        db.commit()

        index_document(doc_id, s_file, text_content, pages=pages)
        created_docs.append(doc_id)

    return {"message": "Sample documents loaded successfully!", "document_ids": created_docs}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
