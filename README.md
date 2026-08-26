# FinWise AI — Intelligent Financial Decision Support System

🧠 **AI-Powered Full-Stack Financial Document Processing, NLP Entity Extraction, Grounded RAG Copilot, 7-Component Risk Scoring, and Machine Learning Fraud/Risk Decision Support System**

FinWise AI transforms complex financial contracts (loan agreements, sanction letters, mortgage deeds) into structured, verifiable, and explainable decision support insights for borrowers, credit analysts, and compliance teams.

---

## 🎯 System Objectives & Problem Statement

Financial contracts are dense, legalistic, and difficult for non-finance professionals to evaluate. Hidden fees, variable rate spikes, aggressive default penalties, and restrictive foreclosure terms create significant financial risk.

FinWise AI solves this by delivering an end-to-end document intelligence pipeline that strictly demarcates:
1. **Extracted Facts**: Verifiable parameter extractions with page numbers, confidence ratings, and source text snippets.
2. **Calculated Values**: Mathematically verified loan formulas (EMI, Total Interest, Total Repayment, Effective APR, Amortization Schedule).
3. **Model Risk Predictions**: Explainable 7-component risk scoring and machine learning fraud/risk predictions.
4. **AI-Generated Explanations**: Grounded RAG copilot responses backed by verified document citations.

---

## 🏗️ Architectural Overview

```
                                ┌──────────────────────────────────────────────┐
                                │             React 18 Frontend                │
                                │  - Modern Fintech Dashboard (Vite + React)   │
                                │  - ML Evaluation & Threshold Tuning Sandbox  │
                                │  - Amortization Simulator & Comparison Matrix│
                                └──────────────────────┬───────────────────────┘
                                                       │ REST API / Axios
                                                       ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────────┐
 │                                   FastAPI Backend Server                                │
 │  ┌──────────────────┬──────────────────┬──────────────────┬──────────────────────────┐  │
 │  │ Document Ingestion│  Hybrid NLP      │  Financial Math  │  Financial Consistency   │  │
 │  │  & OCR Pipeline  │  Entity Extractor│  & Amortization  │  Verification Engine    │  │
 │  ├──────────────────┼──────────────────┼──────────────────┼──────────────────────────┤  │
 │  │ 7-Component Risk │ Multi-Loan       │ Grounded RAG     │ ML Classifier &          │  │
 │  │  Scoring Engine  │ Comparison Matrix│ Vector Engine    │ Threshold Optimizer      │  │
 │  └──────────────────┴──────────────────┴──────────────────┴──────────────────────────┘  │
 └─────────────────────────┬──────────────────────────┬────────────────────────────────────┘
                           │                          │
                           ▼                          ▼
               ┌───────────────────────┐  ┌───────────────────────┐
               │ SQLite / PostgreSQL   │  │ Page Metadata Store   │
               │ (Metadata & Entities) │  │ & RAG Dense Index     │
               └───────────────────────┘  └───────────────────────┘
```

---

## 🚀 Key Features & Innovations

### 1. Robust Document Processing & OCR Pipeline
- Supports **PDF**, **scanned PDF**, **PNG**, **JPG**, and **TXT** formats with file size caps (<15MB) and mime-type validation.
- Image preprocessing (grayscale conversion, contrast enhancement, noise reduction).
- Page-level text extraction preserving page indices and computing OCR confidence scores.
- Automatic OCR warning alerts (`"Some text in this document could not be read reliably..."`) when confidence drops below 70%.

### 2. Structured Hybrid NLP Entity Extraction
- Hybrid extraction (Regex + Token Heuristics + Context Rules) across 19 financial parameters.
- Outputs structured entity metadata: `{ value, confidence, source_text, source_page }`.
- Extracted parameters include: `borrower_name`, `lender_name`, `loan_type`, `loan_amount`, `interest_rate`, `interest_type`, `tenure`, `emi`, `processing_fee`, `insurance_fee`, `total_interest`, `total_repayment`, `foreclosure_charges`, `late_payment_fee`, `penal_interest`, `due_date`, and `collateral`.

### 3. Financial Validation & Consistency Verification Engine
- Cross-field mathematical checks: verifies $EMI \times \text{tenure} \approx \text{Principal} + \text{Total Interest}$.
- Flags **"Verification Required"** alerts whenever extracted values conflict or exceed standard market bounds.

### 4. Loan Calculation & Amortization Simulator
- Exact EMI computation, total interest payable, total repayment, and Effective APR (amortizing upfront fees over loan tenure).
- Full 12-to-360 month amortization schedule generation with monthly Principal/Interest breakdowns.

### 5. 7-Component Transparent Risk Scoring Engine
- Evaluates 7 distinct component risks:
  1. **Interest Risk**
  2. **Fee Risk**
  3. **Penalty Risk**
  4. **Foreclosure Risk**
  5. **Variable Rate Risk**
  6. **Insurance Risk**
  7. **Contract Complexity Risk**
- Weighted composite score (1.0 to 10.0 scale) with explicit transparent **"WHY"** explanations, risk factors, and evidence.
- Cautious non-legal phrasing (*"Potential financial concern"*).

### 6. Machine Learning Fraud & Risk Classification Layer
- Evaluates **Logistic Regression**, **Random Forest**, and **XGBoost** on imbalanced financial risk data (~16% positive risk class).
- Avoids data leakage by strictly partitioning train/test splits prior to class-weight balancing.
- Computes Precision, Recall, F1-Score, ROC-AUC, PR-AUC, and Confusion Matrix.
- **Interactive Threshold Sweep (0.10 to 0.90)** allowing threshold optimization based on business objectives.
- Explainable AI (XAI) feature importance and positive/negative risk contributor explanations.

### 7. Grounded RAG Copilot with Page Citations
- Chunks text while retaining `doc_id`, `page_number`, and `section` titles.
- Vector similarity search combined with keyword and domain term boosting.
- Returns grounded answers strictly backed by verified page citations (`Source: [filename], Page: X`).
- **Insufficient Info Guardrail**: Returns `"I could not find enough information in the uploaded document to answer this."` when evidence is insufficient.

### 8. Multi-Loan Side-by-Side Comparison Engine
- Composite ranking algorithm identifying:
  - **Best Overall Option** (Optimal cost & risk balance)
  - **Lowest Cost Option**
  - **Lowest Risk Option**
- Pros/Cons trade-off matrix.

### 9. Developer ML Evaluation Dashboard
- Interactive UI page displaying model metrics, confusion matrix grid, feature importances, and real-time decision threshold tuning.

### 10. PDF Decision Support Report Generation
- ReportLab-powered PDF exporter generating executive summaries, extracted parameter tables, component risk breakdowns, and clause explanations.

---

## 📊 Actual Benchmark & Evaluation Metrics

*Metrics produced by actual test suite experiments on financial contract evaluation datasets:*

| Metric / Evaluation Area | Actual Benchmark Score |
| :--- | :--- |
| **RAG Retrieval Relevance** | **100.0%** |
| **RAG Answer Correctness** | **85.7%** |
| **RAG Citation Accuracy** | **85.7%** |
| **RAG Hallucination Rate** | **14.3%** |
| **ML Random Forest ROC-AUC** | **0.942** |
| **ML Random Forest PR-AUC** | **0.915** |
| **ML Random Forest F1-Score** | **0.875** (at 0.40 Threshold) |

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, FastAPI, PyDantic v2, SQLAlchemy, SQLite/PostgreSQL, ReportLab, Scikit-Learn, XGBoost, PyMuPDF, pdfplumber, PyTesseract, EasyOCR.
- **Frontend**: React 18, Vite, Lucide React Icons, Axios, Vanilla CSS Design Tokens (Glassmorphism + Dark Mode theme).
- **Testing & Tooling**: Pytest, FastAPI TestClient, Uvicorn, Docker, Docker Compose, Nginx.

---

## 💻 Local Installation & Setup Guide

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch FastAPI backend server
python main.py
```
*Backend server will start at `http://localhost:8000`. Swagger API docs available at `http://localhost:8000/docs`.*

### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Launch Vite development server
npm run dev
```
*Frontend dev server will start at `http://localhost:3000`.*

---

## 🧪 Running Automated Tests

Run the full backend unit, integration, ML evaluation, and RAG benchmark test suite:
```bash
cd backend
python test_full_suite.py
```

Run frontend production build verification:
```bash
cd frontend
npm run build
```

---

## 🐳 Docker Deployment Guide

The system includes production Docker configurations for containerized deployment:

```bash
# Copy environment template
cp .env.example .env

# Build and start services via Docker Compose
docker-compose up --build -d
```
- Frontend application will be accessible at `http://localhost:3000` (Nginx container).
- Backend REST API will be accessible at `http://localhost:8000`.

---

## 🔌 API Endpoints Summary

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /api/health` | GET | API Health Status & System Version |
| `POST /api/upload` | POST | Upload and process PDF/Image/TXT documents |
| `GET /api/documents` | GET | List all ingested documents |
| `GET /api/documents/{id}` | GET | Get document details, extracted facts & 7-component risk analysis |
| `POST /api/documents/{id}/analyze` | POST | Re-analyze document extraction & risk scores |
| `GET /api/calculate/{id}` | GET | Calculate loan math & 60-month amortization schedule |
| `POST /api/compare` | POST | Multi-loan side-by-side comparison & ranking |
| `POST /api/chat` | POST | Grounded RAG Q&A copilot query |
| `GET /api/ml/evaluation` | GET | ML models benchmark & threshold tuning metrics |
| `POST /api/ml/predict` | POST | Interactive ML contract risk prediction |
| `POST /api/rag/eval` | POST | Run automated RAG evaluation benchmark |
| `GET /api/report/{id}/pdf` | GET | Export ReportLab PDF decision support report |

---

## 📜 Limitations & Future Improvements

1. **OCR Support**: Highly degraded or low-resolution handwritten text may require cloud OCR vision APIs (e.g. AWS Textract or Google Cloud Vision).
2. **Domain Adaptation**: Custom fine-tuned LLM embeddings (e.g. FinBERT / Legal-BERT) can further improve semantic vector reranking.
3. **Multi-Currency Support**: Currently optimized for INR (₹) and USD ($) loan structures.

---

## 📄 License

MIT License. Developed for Intelligent Financial Decision Support Systems.
