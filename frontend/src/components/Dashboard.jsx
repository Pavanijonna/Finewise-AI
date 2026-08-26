import React, { useState, useEffect } from 'react';
import { DollarSign, Percent, Calendar, FileText, AlertTriangle, ShieldCheck, Download, Edit2, Check, AlertCircle, Info, RefreshCw, Cpu, Layers } from 'lucide-react';
import ClauseDrawer from './ClauseDrawer';
import { api } from '../services/api';

export default function Dashboard({ docDetail, selectedDocId, documents, onSelectDoc }) {
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    if (docDetail && docDetail.extracted_data) {
      setFormData(docDetail.extracted_data);
    }
  }, [docDetail]);

  if (!docDetail) {
    return (
      <div className="empty-state glass-card animate-fade-in" style={{ margin: '2rem 0', textAlign: 'center', padding: '3rem' }}>
        <FileText size={48} color="#64748b" />
        <h3 style={{ marginTop: '1rem' }}>No Document Selected</h3>
        <p className="text-muted">Please upload a document or click <strong>"Load Sample Docs"</strong> in the navbar to explore FinWise AI.</p>
      </div>
    );
  }

  const ext = formData;
  const risk = docDetail.risk_analysis || {
    overall_risk_score: 5.0,
    risk_level: 'MEDIUM_RISK',
    component_scores: {},
    recommendations: [],
    why_explanation: ''
  };

  const isVerified = ext.validation_status === 'VERIFIED';
  const ocrWarning = docDetail.ocr_warning;
  const ocrConf = docDetail.ocr_confidence || 0.95;

  const riskBadgeClass = 
    risk.risk_level === 'HIGH_RISK' || risk.risk_category === 'HIGH_RISK' ? 'badge-high' :
    risk.risk_level === 'MEDIUM_RISK' || risk.risk_category === 'MEDIUM_RISK' ? 'badge-medium' : 'badge-low';

  const riskScoreVal = risk.overall_risk_score || risk.risk_score || 5.0;

  return (
    <div className="dashboard-container animate-fade-in">
      {/* Top Document Selection & Export Header */}
      <div className="dash-header glass-card">
        <div className="dash-header-info">
          <div className="doc-select-dropdown">
            <label>Active Document:</label>
            <select
              id="dash-doc-select"
              value={selectedDocId || ''}
              onChange={(e) => onSelectDoc(e.target.value)}
              className="input-field"
              style={{ width: 'auto', display: 'inline-block', marginLeft: '0.5rem' }}
            >
              {documents.map(d => (
                <option key={d.id} value={d.id}>{d.filename}</option>
              ))}
            </select>
          </div>
          <h2 className="doc-title" style={{ marginTop: '0.5rem' }}>{docDetail.filename}</h2>
          
          <div className="meta-pills">
            <span className="pill">Borrower: <strong>{ext.borrower_name || 'Valued Borrower'}</strong></span>
            <span className="pill">Lender: <strong>{ext.lender_name || 'Financial Institution'}</strong></span>
            <span className="pill">Type: <strong>{ext.loan_type || 'Personal Loan'} ({ext.interest_type || 'Fixed'})</strong></span>
            <span className="pill">OCR Confidence: <strong>{(ocrConf * 100).toFixed(0)}%</strong></span>
          </div>
        </div>

        <div className="dash-header-actions">
          <a
            id="btn-download-pdf-report"
            href={api.getReportPdfUrl(selectedDocId)}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-primary"
          >
            <Download size={18} />
            <span>Export PDF Report</span>
          </a>
        </div>
      </div>

      {/* OCR & Verification Warning Banners */}
      {ocrWarning && (
        <div className="glass-card glow-high" style={{ margin: '1rem 0', borderLeft: '4px solid #f43f5e' }}>
          <div className="flex-row gap-3 items-center">
            <AlertTriangle size={22} color="#f43f5e" />
            <div>
              <strong style={{ color: '#f43f5e' }}>OCR Quality Alert:</strong> {ocrWarning}
            </div>
          </div>
        </div>
      )}

      {!isVerified && (
        <div className="glass-card glow-high" style={{ margin: '1rem 0', borderLeft: '4px solid #f59e0b' }}>
          <div className="flex-row gap-3 items-center">
            <AlertCircle size={22} color="#f59e0b" />
            <div>
              <strong style={{ color: '#f59e0b' }}>Verification Required:</strong> Extracted financial values exhibit mathematical consistency conflicts. Please review the parameters below.
              {ext.validation_issues && ext.validation_issues.length > 0 && (
                <ul className="small-text" style={{ marginTop: '4px' }}>
                  {ext.validation_issues.map((iss, i) => <li key={i}>{iss}</li>)}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main Grid: 4 Metric Cards Demarcating Facts vs Calculations */}
      <div className="grid-4" style={{ margin: '1.5rem 0' }}>
        <div className="metric-card glass-card">
          <div className="metric-icon bg-cyan">
            <DollarSign size={22} color="#38bdf8" />
          </div>
          <div className="metric-body">
            <div className="flex-row space-between">
              <span className="metric-label">Loan Principal</span>
              <span className="fact-badge">Extracted Fact</span>
            </div>
            <h3 className="metric-value">₹ {floatVal(ext.loan_amount).toLocaleString('en-IN')}</h3>
            <span className="metric-sub">Sanctioned Amount</span>
          </div>
        </div>

        <div className="metric-card glass-card">
          <div className="metric-icon bg-blue">
            <Percent size={22} color="#6366f1" />
          </div>
          <div className="metric-body">
            <div className="flex-row space-between">
              <span className="metric-label">Interest Rate</span>
              <span className="fact-badge">Extracted Fact</span>
            </div>
            <h3 className="metric-value">{floatVal(ext.interest_rate).toFixed(2)}% p.a.</h3>
            <span className="metric-sub">{ext.interest_type || 'Fixed'} Rate</span>
          </div>
        </div>

        <div className="metric-card glass-card">
          <div className="metric-icon bg-purple">
            <Calendar size={22} color="#a855f7" />
          </div>
          <div className="metric-body">
            <div className="flex-row space-between">
              <span className="metric-label">Loan Tenure</span>
              <span className="fact-badge">Extracted Fact</span>
            </div>
            <h3 className="metric-value">{ext.tenure || 60} Months</h3>
            <span className="metric-sub">{(intVal(ext.tenure) / 12).toFixed(1)} Years</span>
          </div>
        </div>

        <div className="metric-card glass-card">
          <div className="metric-icon bg-emerald">
            <DollarSign size={22} color="#10b981" />
          </div>
          <div className="metric-body">
            <div className="flex-row space-between">
              <span className="metric-label">Monthly EMI</span>
              <span className="calc-badge">Calculated Value</span>
            </div>
            <h3 className="metric-value" style={{ color: '#10b981' }}>
              ₹ {floatVal(ext.emi).toLocaleString('en-IN')}
            </h3>
            <span className="metric-sub">Equated Instalment</span>
          </div>
        </div>
      </div>

      {/* Grid: Extracted Parameters vs 7-Component AI Risk Score */}
      <div className="grid-2" style={{ margin: '1.5rem 0' }}>
        {/* Left Column: Extracted Facts & Calculated Values Table */}
        <div className="glass-card">
          <div className="card-header">
            <h3>Extracted Contract Facts & Calculated Math</h3>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setEditing(!editing)}
            >
              {editing ? <Check size={16} /> : <Edit2 size={16} />}
              <span>{editing ? 'Save' : 'Edit Values'}</span>
            </button>
          </div>

          <div className="data-table">
            <div className="data-row">
              <span className="row-label">Processing Fee <span className="fact-badge">Fact</span></span>
              <span className="row-val">₹ {floatVal(ext.processing_fee).toLocaleString('en-IN')} ({floatVal(ext.processing_fee_pct).toFixed(2)}%)</span>
            </div>
            <div className="data-row">
              <span className="row-label">Insurance Premium Fee <span className="fact-badge">Fact</span></span>
              <span className="row-val">₹ {floatVal(ext.insurance_fee).toLocaleString('en-IN')}</span>
            </div>
            <div className="data-row">
              <span className="row-label">Total Interest Payable <span className="calc-badge">Calculated</span></span>
              <span className="row-val" style={{ color: '#f59e0b', fontWeight: 'bold' }}>
                ₹ {floatVal(ext.total_interest).toLocaleString('en-IN')}
              </span>
            </div>
            <div className="data-row">
              <span className="row-label">Total Repayment Amount <span className="calc-badge">Calculated</span></span>
              <span className="row-val" style={{ color: '#38bdf8', fontWeight: 'bold' }}>
                ₹ {floatVal(ext.total_repayment).toLocaleString('en-IN')}
              </span>
            </div>
            <div className="data-row">
              <span className="row-label">Foreclosure Terms <span className="fact-badge">Fact</span></span>
              <span className="row-val">{ext.foreclosure_charges || '3% on principal balance'}</span>
            </div>
            <div className="data-row">
              <span className="row-label">Late Payment Penalties <span className="fact-badge">Fact</span></span>
              <span className="row-val">{ext.late_payment_penalties || '2% per month penal interest'}</span>
            </div>
            <div className="data-row">
              <span className="row-label">Collateral / Security <span className="fact-badge">Fact</span></span>
              <span className="row-val">{ext.collateral || 'Unsecured / No Collateral'}</span>
            </div>
          </div>
        </div>

        {/* Right Column: 7-Component AI Contract Risk Breakdown */}
        <div className="glass-card">
          <div className="card-header">
            <div>
              <h3>AI Risk Model Score</h3>
              <span className="model-badge">Model Prediction</span>
            </div>
            <span className={`badge ${riskBadgeClass}`}>
              {(risk.risk_level || risk.risk_category).replace('_', ' ')}
            </span>
          </div>

          <div className="risk-score-box">
            <div className="score-number-display">
              <span className="score-num">{riskScoreVal.toFixed(1)}</span>
              <span className="score-max">/ 10</span>
            </div>
            <div className="score-meter-bar">
              <div
                className="score-fill"
                style={{
                  width: `${(riskScoreVal / 10) * 100}%`,
                  background: riskScoreVal > 7 ? '#f43f5e' : riskScoreVal > 4.5 ? '#f59e0b' : '#10b981'
                }}
              />
            </div>
          </div>

          {/* Rationale Explanation ("WHY") */}
          <div className="why-box" style={{ margin: '1rem 0', padding: '0.75rem', background: '#0f172a', borderRadius: '8px', borderLeft: '3px solid #38bdf8' }}>
            <span className="font-bold small-text" style={{ color: '#38bdf8' }}>Why this Risk Score was generated:</span>
            <p className="small-text" style={{ color: '#cbd5e1', marginTop: '4px' }}>
              {risk.why_explanation || "Derived from weighted 7-component evaluation."}
            </p>
          </div>

          {/* 7-Component Risk Scores */}
          {risk.component_scores && (
            <div className="component-risk-list">
              <span className="font-bold small-text">7-Component Risk Scores:</span>
              <div className="grid-2" style={{ gap: '0.5rem', marginTop: '0.5rem' }}>
                {Object.entries(risk.component_scores).map(([compKey, compObj]) => (
                  <div key={compKey} className="comp-score-chip">
                    <span className="comp-name">{compKey.replace('_', ' ').title ? compKey.replace('_', ' ') : compKey}:</span>
                    <span className="comp-val font-bold" style={{ color: compObj.score >= 7 ? '#f43f5e' : compObj.score >= 5 ? '#f59e0b' : '#10b981' }}>
                      {compObj.score.toFixed(1)} / 10
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="recommendations-box" style={{ marginTop: '1rem' }}>
            <span className="font-bold small-text"><ShieldCheck size={16} color="#38bdf8" /> Key Borrower Recommendations:</span>
            <ul style={{ marginTop: '0.4rem' }}>
              {risk.recommendations && risk.recommendations.map((rec, i) => (
                <li key={i} className="small-text">{rec}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* AI Explanation Cautionary Disclaimer */}
      <div className="glass-card" style={{ margin: '1rem 0', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #334155' }}>
        <div className="flex-row gap-3 items-center">
          <Info size={20} color="#64748b" />
          <span className="small-text text-muted">
            <strong>AI Explanation Notice:</strong> Content in this dashboard distinguishes between verified extracted facts, calculated loan formulas, machine learning risk predictions, and AI-generated explanations. AI output does not constitute legal or financial advice.
          </span>
        </div>
      </div>

      {/* Classified Financial Clauses Section */}
      <ClauseDrawer clauses={docDetail.clauses || []} />
    </div>
  );
}

function floatVal(v) {
  const parsed = parseFloat(v);
  return isNaN(parsed) ? 0 : parsed;
}

function intVal(v) {
  const parsed = parseInt(v, 10);
  return isNaN(parsed) ? 0 : parsed;
}
