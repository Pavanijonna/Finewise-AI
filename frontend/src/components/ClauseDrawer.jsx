import React from 'react';
import { AlertCircle, ShieldAlert, CheckCircle2, HelpCircle, FileText } from 'lucide-react';

export default function ClauseDrawer({ clauses }) {
  if (!clauses || clauses.length === 0) {
    return (
      <div className="glass-card" style={{ marginTop: '1.5rem' }}>
        <h3>Classified Contract Clauses</h3>
        <p className="text-muted">No specific risk clauses flagged for this document.</p>
      </div>
    );
  }

  return (
    <div className="clause-drawer-section glass-card" style={{ marginTop: '1.5rem' }}>
      <div className="section-header-inline">
        <div>
          <h3>Clause Detection Engine & <span className="gradient-text">Plain-Language Explanations</span></h3>
          <p className="subtitle">Classified contract clauses translated into simple, non-expert terms.</p>
        </div>
      </div>

      <div className="grid-2" style={{ marginTop: '1rem' }}>
        {clauses.map((item, idx) => {
          const isHigh = item.risk_level === 'HIGH_RISK';
          const isMed = item.risk_level === 'MEDIUM_RISK';
          const badgeClass = isHigh ? 'badge-high' : isMed ? 'badge-medium' : 'badge-low';

          return (
            <div key={idx} className={`clause-card glass-card ${isHigh ? 'border-rose' : ''}`}>
              <div className="clause-card-header">
                <div className="clause-title-group">
                  {isHigh ? <ShieldAlert size={20} color="#f43f5e" /> : <FileText size={20} color="#38bdf8" />}
                  <h4>{item.title}</h4>
                </div>
                <span className={`badge ${badgeClass}`}>{item.risk_level.replace('_', ' ')}</span>
              </div>

              <div className="clause-snippet-box">
                <span className="snippet-label">Exact Contract Snippet:</span>
                <p className="snippet-text">"{item.text_snippet}"</p>
              </div>

              <div className="clause-explanation-box">
                <div className="exp-header">
                  <HelpCircle size={16} color="#a855f7" />
                  <span>Simple Explanation (for Non-Finance Users):</span>
                </div>
                <p className="exp-text">{item.simple_explanation}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
