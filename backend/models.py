import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="UPLOADED") # UPLOADED, PROCESSED, ERROR
    text_content = Column(Text, nullable=True)
    ocr_confidence = Column(Float, default=1.0)
    ocr_warning = Column(Text, nullable=True)
    page_count = Column(Integer, default=1)

    extracted_data = relationship("ExtractedData", back_populates="document", uselist=False, cascade="all, delete-orphan")
    clauses = relationship("Clause", back_populates="document", cascade="all, delete-orphan")
    risk_analysis = relationship("RiskAnalysisRecord", back_populates="document", uselist=False, cascade="all, delete-orphan")

class ExtractedData(Base):
    __tablename__ = "extracted_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, ForeignKey("documents.id"), nullable=False, unique=True)
    borrower_name = Column(String, nullable=True)
    lender_name = Column(String, nullable=True)
    loan_type = Column(String, nullable=True)
    loan_amount = Column(Float, nullable=True)
    interest_rate = Column(Float, nullable=True)
    interest_type = Column(String, default="Fixed") # Fixed or Floating
    tenure_months = Column(Integer, nullable=True)
    emi = Column(Float, nullable=True)
    processing_fee = Column(Float, nullable=True)
    processing_fee_pct = Column(Float, nullable=True)
    insurance_fee = Column(Float, nullable=True)
    total_interest = Column(Float, nullable=True)
    total_repayment = Column(Float, nullable=True)
    foreclosure_charges = Column(String, nullable=True)
    late_penalty = Column(String, nullable=True)
    due_dates = Column(String, nullable=True)
    collateral = Column(String, nullable=True)
    validation_status = Column(String, default="VERIFIED") # VERIFIED or VERIFICATION_REQUIRED
    validation_issues = Column(JSON, nullable=True)
    raw_json = Column(JSON, nullable=True)

    document = relationship("Document", back_populates="extracted_data")

class Clause(Base):
    __tablename__ = "clauses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, ForeignKey("documents.id"), nullable=False)
    title = Column(String, nullable=False)
    clause_type = Column(String, nullable=False) # Interest, Penalty, Prepayment, Insurance, Hidden
    text_snippet = Column(Text, nullable=False)
    risk_level = Column(String, nullable=False) # HIGH_RISK, MEDIUM_RISK, LOW_RISK
    simple_explanation = Column(Text, nullable=False)
    impact_score = Column(Float, default=5.0)
    page_number = Column(Integer, default=1)

    document = relationship("Document", back_populates="clauses")

class RiskAnalysisRecord(Base):
    __tablename__ = "risk_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, ForeignKey("documents.id"), nullable=False, unique=True)
    overall_risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False) # HIGH_RISK, MEDIUM_RISK, LOW_RISK
    component_scores = Column(JSON, nullable=False)
    risk_factors = Column(JSON, nullable=False)
    evidence = Column(JSON, nullable=False)
    recommendations = Column(JSON, nullable=False)

    document = relationship("Document", back_populates="risk_analysis")

class ComparisonReport(Base):
    __tablename__ = "comparison_reports"

    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    comparison_json = Column(JSON, nullable=False)
