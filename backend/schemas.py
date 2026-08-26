from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    upload_time: datetime
    status: str
    ocr_confidence: float = 1.0
    ocr_warning: Optional[str] = None
    text_snippet: Optional[str] = None

    class Config:
        from_attributes = True

class ExtractedDataSchema(BaseModel):
    borrower_name: Optional[str] = "Valued Borrower"
    lender_name: Optional[str] = "Financial Institution"
    loan_type: Optional[str] = "Personal Loan"
    loan_amount: Optional[float] = 0.0
    interest_rate: Optional[float] = 0.0
    interest_type: Optional[str] = "Fixed"
    tenure: Optional[int] = 0
    emi: Optional[float] = 0.0
    processing_fee: Optional[float] = 0.0
    processing_fee_pct: Optional[float] = 0.0
    insurance_fee: Optional[float] = 0.0
    total_interest: Optional[float] = 0.0
    total_repayment: Optional[float] = 0.0
    foreclosure_charges: Optional[str] = "Standard"
    late_payment_penalties: Optional[str] = "Standard"
    due_dates: Optional[str] = "5th of every month"
    collateral: Optional[str] = "Unsecured"
    validation_status: Optional[str] = "VERIFIED"
    validation_issues: Optional[List[str]] = []
    structured_entities: Optional[Dict[str, Any]] = None

class ClauseSchema(BaseModel):
    id: Optional[int] = None
    title: str
    clause_type: str
    text_snippet: str
    risk_level: str  # HIGH_RISK, MEDIUM_RISK, LOW_RISK
    simple_explanation: str
    impact_score: float = 5.0
    page_number: int = 1

class FinancialCalculationResponse(BaseModel):
    doc_id: str
    loan_amount: float
    annual_interest_rate: float
    tenure_months: int
    calculated_emi: float
    total_interest_payable: float
    total_repayment_amount: float
    processing_fee: float
    processing_fee_percentage: float
    effective_apr: float
    amortization_schedule: List[Dict[str, Any]]

class ComponentRiskSchema(BaseModel):
    score: float
    explanation: str

class RiskAnalysisResponse(BaseModel):
    doc_id: str
    overall_risk_score: float
    risk_score: float
    risk_level: str
    risk_category: str
    component_scores: Dict[str, ComponentRiskSchema]
    risk_factors: List[str]
    evidence: List[Dict[str, Any]]
    recommendations: List[str]
    why_explanation: str

class ComparisonRequest(BaseModel):
    doc_ids: Optional[List[str]] = None

class LoanComparisonItem(BaseModel):
    doc_id: str
    filename: str
    borrower_name: str
    loan_amount: float
    interest_rate: float
    interest_type: str
    tenure_months: int
    emi: float
    processing_fee: float
    total_interest: float
    total_repayment: float
    effective_total_cost: float
    foreclosure_charges: str
    late_penalty: str
    risk_score: float
    overall_rank: int
    composite_score: float
    pros: List[str]
    cons: List[str]

class ComparisonResponse(BaseModel):
    comparison_id: str
    timestamp: datetime
    compared_loans: List[LoanComparisonItem]
    best_option_doc_id: str
    best_option_name: str
    recommendation_reasoning: str
    lowest_cost_doc_id: str
    lowest_risk_doc_id: str

class ChatRequest(BaseModel):
    doc_ids: Optional[List[str]] = None
    query: str

class ChatSourceItem(BaseModel):
    doc_id: str
    filename: str
    page_number: int
    section: str
    citation: str
    snippet: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSourceItem]
    confidence_score: float
    grounded: bool = True
    disclaimer: Optional[str] = None

class MLPredictRequest(BaseModel):
    dti: float = 0.35
    interest_rate: float = 10.5
    processing_fee_pct: float = 0.5
    penal_rate: float = 24.0
    credit_score_norm: float = 0.70
    has_foreclosure_penalty: bool = True
    is_floating_rate: bool = False
    has_mandatory_insurance: bool = False
    decision_threshold: float = 0.50
    model_name: str = "Random Forest"

class MLPredictResponse(BaseModel):
    model_name: str
    risk_probability: float
    prediction_class: str
    decision_threshold: float
    positive_risk_factors: List[str]
    negative_risk_factors: List[str]
    explainable_statement: str
