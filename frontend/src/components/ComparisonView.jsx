import React, { useState, useEffect } from 'react';
import { GitCompare, Trophy, Award, DollarSign, ShieldCheck, CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react';
import { api } from '../services/api';

export default function ComparisonView({ documents, onSelectDoc }) {
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    runComparison();
  }, [documents]);

  const runComparison = async () => {
    if (documents.length === 0) return;
    setLoading(true);
    setError(null);
    try {
      const docIds = documents.map(d => d.id);
      const res = await api.compareLoans(docIds);
      setComparisonData(res);
    } catch (err) {
      setError('Failed to compute multi-loan comparison matrix.');
    } finally {
      setLoading(false);
    }
  };

  if (documents.length < 2) {
    return (
      <div className="glass-card animate-fade-in" style={{ margin: '2rem 0', textAlign: 'center', padding: '3rem' }}>
        <GitCompare size={48} color="#38bdf8" />
        <h3 style={{ marginTop: '1rem' }}>Multi-Loan Comparison Engine</h3>
        <p className="text-muted" style={{ maxWidth: '550px', margin: '0.5rem auto' }}>
          Upload at least 2 loan documents (or click <strong>"Load Sample Docs"</strong> in the navbar) to compare interest rates, EMIs, total repayment costs, risk scores, and view automated AI ranking.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="glass-card text-center" style={{ padding: '3rem' }}>
        <div className="spinner"></div>
        <p style={{ marginTop: '1rem' }}>Running multi-criteria financial comparison matrix & risk ranking...</p>
      </div>
    );
  }

  if (error || !comparisonData) {
    return (
      <div className="glass-card" style={{ margin: '2rem 0' }}>
        <AlertTriangle size={36} color="#f43f5e" />
        <p>{error || 'No comparison data generated.'}</p>
      </div>
    );
  }

  const loans = comparisonData.compared_loans || [];

  return (
    <div className="comparison-container animate-fade-in">
      <div className="section-header">
        <h2>Multi-Loan <span className="gradient-text">Comparison & Ranking Engine</span></h2>
        <p className="subtitle">Side-by-side evaluation of loan offers ranked by total effective cost, contract flexibility, and risk score.</p>
      </div>

      {/* Best Recommendation Banner */}
      <div className="recommendation-banner glass-card glow-cyan">
        <div className="rec-badge">
          <Trophy size={28} color="#f59e0b" />
          <div>
            <span className="rec-tag font-bold">RECOMMENDED OPTION</span>
            <h3 className="rec-title">{comparisonData.best_option_name}</h3>
          </div>
        </div>
        <div className="rec-body">
          <p>{comparisonData.recommendation_reasoning}</p>
        </div>
      </div>

      {/* Comparison Matrix Table */}
      <div className="glass-card table-responsive" style={{ margin: '1.5rem 0' }}>
        <table className="comparison-table">
          <thead>
            <tr>
              <th>Financial Parameter</th>
              {loans.map(loan => (
                <th key={loan.doc_id} className={loan.doc_id === comparisonData.best_option_doc_id ? 'col-highlight' : ''}>
                  <div className="th-loan-name">{loan.filename}</div>
                  <div className="th-rank-pill">
                    {loan.doc_id === comparisonData.best_option_doc_id ? (
                      <span className="rank-badge rank-1"><Award size={14} /> Rank #1 Best Choice</span>
                    ) : (
                      <span className="rank-badge">Rank #{loan.overall_rank}</span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="param-label">Borrower Name</td>
              {loans.map(l => <td key={l.doc_id}><strong>{l.borrower_name}</strong></td>)}
            </tr>
            <tr>
              <td className="param-label">Loan Principal</td>
              {loans.map(l => <td key={l.doc_id}>₹ {l.loan_amount.toLocaleString('en-IN')}</td>)}
            </tr>
            <tr>
              <td className="param-label">Annual Interest Rate</td>
              {loans.map(l => (
                <td key={l.doc_id} className={l.interest_rate <= 9.0 ? 'val-green' : ''}>
                  <strong>{l.interest_rate.toFixed(2)}%</strong> ({l.interest_type})
                </td>
              ))}
            </tr>
            <tr>
              <td className="param-label">Monthly EMI</td>
              {loans.map(l => <td key={l.doc_id} style={{ color: '#10b981', fontWeight: 'bold' }}>₹ {l.emi.toLocaleString('en-IN')}</td>)}
            </tr>
            <tr>
              <td className="param-label">Upfront Processing Fee</td>
              {loans.map(l => <td key={l.doc_id}>₹ {l.processing_fee.toLocaleString('en-IN')}</td>)}
            </tr>
            <tr>
              <td className="param-label">Total Interest Payable</td>
              {loans.map(l => <td key={l.doc_id} style={{ color: '#f59e0b' }}>₹ {l.total_interest.toLocaleString('en-IN')}</td>)}
            </tr>
            <tr>
              <td className="param-label">Total Repayment Amount</td>
              {loans.map(l => (
                <td key={l.doc_id} style={{ color: '#38bdf8', fontWeight: 'bold' }}>
                  ₹ {l.total_repayment.toLocaleString('en-IN')}
                </td>
              ))}
            </tr>
            <tr>
              <td className="param-label">Foreclosure Charges</td>
              {loans.map(l => <td key={l.doc_id} className="small-text">{l.foreclosure_charges}</td>)}
            </tr>
            <tr>
              <td className="param-label">Contract Risk Score</td>
              {loans.map(l => (
                <td key={l.doc_id}>
                  <span className={`badge ${l.risk_score > 7 ? 'badge-high' : l.risk_score > 4 ? 'badge-medium' : 'badge-low'}`}>
                    {l.risk_score} / 10
                  </span>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>

      {/* Pros & Cons Cards */}
      <div className="grid-3" style={{ margin: '1.5rem 0' }}>
        {loans.map(l => (
          <div key={l.doc_id} className="glass-card">
            <h4>{l.filename}</h4>
            <span className="text-muted" style={{ fontSize: '0.8rem' }}>Borrower: {l.borrower_name}</span>

            <div className="pro-con-group" style={{ marginTop: '1rem' }}>
              <div className="pro-list">
                <span className="pro-title"><CheckCircle size={14} color="#10b981" /> Advantages:</span>
                <ul>
                  {l.pros && l.pros.map((p, i) => <li key={i}>{p}</li>)}
                </ul>
              </div>

              <div className="con-list" style={{ marginTop: '0.75rem' }}>
                <span className="con-title"><AlertTriangle size={14} color="#f43f5e" /> Trade-offs / Risks:</span>
                <ul>
                  {l.cons && l.cons.map((c, i) => <li key={i}>{c}</li>)}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
