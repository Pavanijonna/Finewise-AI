import React, { useState, useEffect } from 'react';
import { Cpu, Sliders, AlertCircle, BarChart2, ShieldAlert, CheckCircle, RefreshCw, Zap } from 'lucide-react';
import { api } from '../services/api';

export default function MLEvaluationView() {
  const [threshold, setThreshold] = useState(0.50);
  const [modelData, setModelData] = useState(null);
  const [selectedModel, setSelectedModel] = useState('Random Forest');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Live predictor form state
  const [predInput, setPredInput] = useState({
    dti: 0.40,
    interest_rate: 14.5,
    processing_fee_pct: 2.0,
    penal_rate: 28.0,
    credit_score_norm: 0.60,
    has_foreclosure_penalty: true,
    is_floating_rate: true,
    has_mandatory_insurance: true,
    decision_threshold: 0.50,
    model_name: 'Random Forest'
  });
  const [predResult, setPredResult] = useState(null);
  const [predicting, setPredicting] = useState(false);

  useEffect(() => {
    fetchEvaluation(threshold);
  }, [threshold]);

  const fetchEvaluation = async (th) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getMLEvaluation(th);
      setModelData(data);
    } catch (err) {
      console.error('Failed to load ML evaluation:', err);
      setError('Failed to fetch ML model evaluation metrics.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunPrediction = async () => {
    setPredicting(true);
    try {
      const res = await api.predictRiskML({ ...predInput, decision_threshold: threshold, model_name: selectedModel });
      setPredResult(res);
    } catch (err) {
      console.error('ML Prediction error:', err);
    } finally {
      setPredicting(false);
    }
  };

  if (loading && !modelData) {
    return (
      <div className="glass-card text-center" style={{ padding: '3rem', margin: '2rem 0' }}>
        <div className="spinner"></div>
        <p style={{ marginTop: '1rem' }}>Evaluating ML Risk Models (Logistic Regression, Random Forest, XGBoost)...</p>
      </div>
    );
  }

  if (error || !modelData) {
    return (
      <div className="glass-card text-center" style={{ padding: '3rem', margin: '2rem 0' }}>
        <AlertCircle size={48} color="#f43f5e" />
        <h3>Evaluation Failed</h3>
        <p>{error || 'Failed to load model metrics.'}</p>
        <button className="btn btn-primary" onClick={() => fetchEvaluation(threshold)} style={{ marginTop: '1rem' }}>
          <RefreshCw size={16} /> Retry Evaluation
        </button>
      </div>
    );
  }

  const currentModel = modelData.models[selectedModel] || modelData.models['Random Forest'] || {};
  const sweep = currentModel.threshold_sweep || [];
  const featImportances = currentModel.feature_importance || {};

  return (
    <div className="ml-eval-container animate-fade-in">
      <div className="section-header">
        <h2>ML Risk Model <span className="gradient-text">Evaluation & Threshold Tuning</span></h2>
        <p className="subtitle">Developer & Admin Model Benchmark: Imbalanced Data Metrics, Precision-Recall Trade-offs, and Explainable AI Controls.</p>
      </div>

      {/* Deceptive Accuracy Alert Banner */}
      <div className="glass-card glow-cyan" style={{ margin: '1rem 0', borderLeft: '4px solid #38bdf8' }}>
        <div className="flex-row gap-3">
          <AlertCircle size={24} color="#38bdf8" />
          <div>
            <h4 style={{ color: '#38bdf8', marginBottom: '0.25rem' }}>Important: Why Accuracy Alone is Deceptive for Imbalanced Financial Data</h4>
            <p className="small-text" style={{ color: '#cbd5e1' }}>
              {modelData.dataset_info.imbalanced_explanation} In this experiment, positive risk/fraud cases represent 
              <strong> ~{(modelData.dataset_info.positive_class_ratio * 100).toFixed(1)}%</strong> of loans. We optimize for <strong>F1-Score, Precision, Recall, and PR-AUC</strong> rather than naive accuracy.
            </p>
          </div>
        </div>
      </div>

      {/* Model Selector & Config Bar */}
      <div className="glass-card flex-row space-between items-center" style={{ margin: '1.5rem 0', flexWrap: 'wrap', gap: '1rem' }}>
        <div className="flex-row items-center gap-3">
          <Cpu size={22} color="#a855f7" />
          <label className="font-bold">Select Trained ML Model:</label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="input-field"
            style={{ width: 'auto', minWidth: '180px' }}
          >
            {Object.keys(modelData.models).map(name => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
        </div>

        {/* Interactive Threshold Slider */}
        <div className="flex-row items-center gap-3" style={{ minWidth: '320px', flex: 1 }}>
          <Sliders size={20} color="#38bdf8" />
          <label className="font-bold">Decision Threshold:</label>
          <input
            type="range"
            min="0.10"
            max="0.90"
            step="0.05"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="range-input"
            style={{ flex: 1 }}
          />
          <span className="badge badge-medium" style={{ fontSize: '1rem', minWidth: '55px', textAlign: 'center' }}>
            {threshold.toFixed(2)}
          </span>
        </div>
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid-4" style={{ margin: '1.5rem 0' }}>
        <div className="metric-card glass-card">
          <span className="metric-label">Precision</span>
          <h3 className="metric-value" style={{ color: '#10b981' }}>{(currentModel.precision * 100).toFixed(1)}%</h3>
          <span className="metric-sub">True Positives / Predicted Positives</span>
        </div>

        <div className="metric-card glass-card">
          <span className="metric-label">Recall (Sensitivity)</span>
          <h3 className="metric-value" style={{ color: '#38bdf8' }}>{(currentModel.recall * 100).toFixed(1)}%</h3>
          <span className="metric-sub">True Positives / Actual Positives</span>
        </div>

        <div className="metric-card glass-card">
          <span className="metric-label">F1 Score</span>
          <h3 className="metric-value" style={{ color: '#f59e0b' }}>{(currentModel.f1 * 100).toFixed(1)}%</h3>
          <span className="metric-sub">Harmonic Mean of Precision & Recall</span>
        </div>

        <div className="metric-card glass-card">
          <span className="metric-label">ROC-AUC / PR-AUC</span>
          <h3 className="metric-value" style={{ color: '#a855f7' }}>
            {currentModel.roc_auc.toFixed(3)} <span style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>({currentModel.pr_auc.toFixed(3)})</span>
          </h3>
          <span className="metric-sub">ROC-AUC (PR-AUC)</span>
        </div>
      </div>

      {/* Grid: Confusion Matrix & Feature Importances */}
      <div className="grid-2" style={{ margin: '1.5rem 0' }}>
        {/* Confusion Matrix Card */}
        <div className="glass-card">
          <div className="card-header">
            <h3>Confusion Matrix (Threshold = {threshold.toFixed(2)})</h3>
          </div>
          {currentModel.confusion_matrix && (
            <div className="cm-grid">
              <div className="cm-box cm-tn">
                <span className="cm-val">{currentModel.confusion_matrix[0][0]}</span>
                <span className="cm-lbl">True Negative (TN)</span>
                <span className="cm-desc">Low Risk correctly identified</span>
              </div>
              <div className="cm-box cm-fp">
                <span className="cm-val">{currentModel.confusion_matrix[0][1]}</span>
                <span className="cm-lbl">False Positive (FP)</span>
                <span className="cm-desc">Low Risk flagged incorrectly</span>
              </div>
              <div className="cm-box cm-fn">
                <span className="cm-val">{currentModel.confusion_matrix[1][0]}</span>
                <span className="cm-lbl">False Negative (FN)</span>
                <span className="cm-desc">High Risk MISSED (Dangerous)</span>
              </div>
              <div className="cm-box cm-tp">
                <span className="cm-val">{currentModel.confusion_matrix[1][1]}</span>
                <span className="cm-lbl">True Positive (TP)</span>
                <span className="cm-desc">High Risk correctly flagged</span>
              </div>
            </div>
          )}
        </div>

        {/* Feature Importance Chart */}
        <div className="glass-card">
          <div className="card-header">
            <h3>Top Contributing Risk Features</h3>
          </div>
          <div className="feat-list">
            {Object.entries(featImportances).map(([feat, score]) => (
              <div key={feat} className="feat-item" style={{ margin: '0.6rem 0' }}>
                <div className="flex-row space-between small-text">
                  <span>{feat}</span>
                  <span className="font-bold">{(score * 100).toFixed(1)}%</span>
                </div>
                <div className="score-meter-bar" style={{ height: '8px', marginTop: '4px' }}>
                  <div className="score-fill" style={{ width: `${Math.min(100, score * 250)}%`, background: '#38bdf8' }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Threshold Sweep Trade-off Table */}
      <div className="glass-card" style={{ margin: '1.5rem 0' }}>
        <div className="card-header">
          <h3>Decision Threshold Tuning Sweep</h3>
          <span className="text-muted small-text">Compare metrics across decision thresholds (0.10 - 0.90)</span>
        </div>
        <div className="table-responsive">
          <table className="comparison-table">
            <thead>
              <tr>
                <th>Threshold</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1 Score</th>
                <th>True Positives (TP)</th>
                <th>False Positives (FP)</th>
                <th>False Negatives (FN)</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {sweep.map((row) => (
                <tr key={row.threshold} className={Math.abs(row.threshold - threshold) < 0.01 ? 'col-highlight' : ''}>
                  <td><strong>{row.threshold.toFixed(2)}</strong></td>
                  <td style={{ color: '#10b981' }}>{(row.precision * 100).toFixed(1)}%</td>
                  <td style={{ color: '#38bdf8' }}>{(row.recall * 100).toFixed(1)}%</td>
                  <td style={{ color: '#f59e0b', fontWeight: 'bold' }}>{(row.f1 * 100).toFixed(1)}%</td>
                  <td>{row.tp}</td>
                  <td>{row.fp}</td>
                  <td style={{ color: '#f43f5e' }}>{row.fn}</td>
                  <td>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => setThreshold(row.threshold)}
                    >
                      Apply {row.threshold.toFixed(2)}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Live Single Contract ML Predictor Sandbox */}
      <div className="glass-card glow-purple" style={{ margin: '1.5rem 0' }}>
        <div className="card-header">
          <h3><Zap size={20} color="#a855f7" /> Interactive ML Contract Risk Sandbox</h3>
          <button className="btn btn-primary" onClick={handleRunPrediction} disabled={predicting}>
            {predicting ? 'Evaluating...' : 'Run ML Risk Prediction'}
          </button>
        </div>

        <div className="grid-3" style={{ margin: '1rem 0' }}>
          <div>
            <label className="small-text">Debt-to-Income (DTI): {predInput.dti.toFixed(2)}</label>
            <input
              type="range" min="0.10" max="0.75" step="0.05"
              value={predInput.dti}
              onChange={(e) => setPredInput(p => ({ ...p, dti: parseFloat(e.target.value) }))}
              className="range-input"
            />
          </div>
          <div>
            <label className="small-text">Interest Rate (%): {predInput.interest_rate.toFixed(1)}%</label>
            <input
              type="range" min="5.0" max="25.0" step="0.5"
              value={predInput.interest_rate}
              onChange={(e) => setPredInput(p => ({ ...p, interest_rate: parseFloat(e.target.value) }))}
              className="range-input"
            />
          </div>
          <div>
            <label className="small-text">Processing Fee (%): {predInput.processing_fee_pct.toFixed(1)}%</label>
            <input
              type="range" min="0.5" max="5.0" step="0.25"
              value={predInput.processing_fee_pct}
              onChange={(e) => setPredInput(p => ({ ...p, processing_fee_pct: parseFloat(e.target.value) }))}
              className="range-input"
            />
          </div>
        </div>

        {predResult && (
          <div className="glass-card" style={{ background: '#0f172a', marginTop: '1rem' }}>
            <div className="flex-row space-between items-center">
              <h4>Prediction Result ({predResult.model_name}):</h4>
              <span className={`badge ${predResult.prediction_class === 'HIGH_RISK' ? 'badge-high' : 'badge-low'}`}>
                {predResult.prediction_class} ({(predResult.risk_probability * 100).toFixed(1)}% Prob)
              </span>
            </div>
            <p className="small-text" style={{ margin: '0.5rem 0', color: '#cbd5e1' }}>
              {predResult.explainable_statement}
            </p>
            <div className="grid-2" style={{ marginTop: '0.75rem' }}>
              <div>
                <span className="font-bold small-text" style={{ color: '#f43f5e' }}>Positive Risk Factors:</span>
                <ul className="small-text">
                  {predResult.positive_risk_factors.map((f, i) => <li key={i}>{f}</li>)}
                </ul>
              </div>
              <div>
                <span className="font-bold small-text" style={{ color: '#10b981' }}>Mitigating Risk Factors:</span>
                <ul className="small-text">
                  {predResult.negative_risk_factors.map((f, i) => <li key={i}>{f}</li>)}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
