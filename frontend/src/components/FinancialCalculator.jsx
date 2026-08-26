import React, { useState, useEffect } from 'react';
import { Calculator, DollarSign, Percent, Calendar, PieChart, Download } from 'lucide-react';
import { api } from '../services/api';

export default function FinancialCalculator({ docDetail }) {
  const [amount, setAmount] = useState(500000);
  const [rate, setRate] = useState(10.5);
  const [tenure, setTenure] = useState(60);
  const [processingFee, setProcessingFee] = useState(2500);

  const [calcResult, setCalcResult] = useState(null);

  useEffect(() => {
    if (docDetail && docDetail.extracted_data) {
      const ext = docDetail.extracted_data;
      if (ext.loan_amount) setAmount(ext.loan_amount);
      if (ext.interest_rate) setRate(ext.interest_rate);
      if (ext.tenure) setTenure(ext.tenure);
      if (ext.processing_fee) setProcessingFee(ext.processing_fee);
    }
  }, [docDetail]);

  useEffect(() => {
    computeMath();
  }, [amount, rate, tenure, processingFee]);

  const computeMath = () => {
    const P = parseFloat(amount) || 0;
    const annualRate = parseFloat(rate) || 0;
    const n = parseInt(tenure, 10) || 1;
    const fee = parseFloat(processingFee) || 0;

    const r = (annualRate / 100) / 12;
    let emi = 0;
    if (r > 0 && n > 0) {
      emi = P * r * Math.pow(1 + r, n) / (Math.pow(1 + r, n) - 1);
    } else {
      emi = P / n;
    }

    const totalRepayment = emi * n;
    const totalInterest = totalRepayment - P;
    const feePct = P > 0 ? (fee / P) * 100 : 0;
    const apr = annualRate + (feePct / (n / 12));

    const schedule = [];
    let balance = P;
    for (let m = 1; m <= Math.min(n, 120); m++) {
      const intComp = balance * r;
      const prinComp = emi - intComp;
      balance = Math.max(0, balance - prinComp);
      schedule.append ? null : schedule.push({
        month: m,
        installment: emi,
        principal: prinComp,
        interest: intComp,
        balance: balance
      });
    }

    setCalcResult({
      emi: emi,
      totalRepayment: totalRepayment,
      totalInterest: totalInterest,
      feePct: feePct,
      apr: apr,
      schedule: schedule
    });
  };

  return (
    <div className="calculator-container animate-fade-in">
      <div className="section-header">
        <h2>Financial Calculator & <span className="gradient-text">Amortization Simulator</span></h2>
        <p className="subtitle">Interactive slider controls to model loan repayment structures, total interest impact, and effective annual rates.</p>
      </div>

      <div className="grid-2" style={{ margin: '1.5rem 0' }}>
        {/* Slider Controls */}
        <div className="glass-card">
          <h3>Loan Parameters Simulator</h3>

          {/* Amount Slider */}
          <div className="slider-group">
            <div className="slider-label-row">
              <label>Loan Amount (Principal):</label>
              <span className="slider-val">₹ {amount.toLocaleString('en-IN')}</span>
            </div>
            <input
              id="slider-amount"
              type="range"
              min="50000"
              max="5000000"
              step="25000"
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              className="range-input"
            />
          </div>

          {/* Interest Rate Slider */}
          <div className="slider-group">
            <div className="slider-label-row">
              <label>Annual Interest Rate (%):</label>
              <span className="slider-val">{rate.toFixed(2)}%</span>
            </div>
            <input
              id="slider-rate"
              type="range"
              min="5.0"
              max="24.0"
              step="0.25"
              value={rate}
              onChange={(e) => setRate(Number(e.target.value))}
              className="range-input"
            />
          </div>

          {/* Tenure Slider */}
          <div className="slider-group">
            <div className="slider-label-row">
              <label>Tenure (Months):</label>
              <span className="slider-val">{tenure} Months ({ (tenure / 12).toFixed(1) } Yrs)</span>
            </div>
            <input
              id="slider-tenure"
              type="range"
              min="6"
              max="360"
              step="6"
              value={tenure}
              onChange={(e) => setTenure(Number(e.target.value))}
              className="range-input"
            />
          </div>

          {/* Upfront Processing Fee */}
          <div className="slider-group">
            <div className="slider-label-row">
              <label>Processing Fee (Upfront):</label>
              <span className="slider-val">₹ {processingFee.toLocaleString('en-IN')}</span>
            </div>
            <input
              id="slider-fee"
              type="range"
              min="0"
              max="25000"
              step="500"
              value={processingFee}
              onChange={(e) => setProcessingFee(Number(e.target.value))}
              className="range-input"
            />
          </div>
        </div>

        {/* Calculation Metrics Summary Card */}
        {calcResult && (
          <div className="glass-card glow-blue">
            <h3>Calculated Loan Breakdown</h3>

            <div className="calc-emi-hero">
              <span className="hero-label">Equated Monthly Instalment (EMI)</span>
              <h2 className="hero-value">₹ {Math.round(calcResult.emi).toLocaleString('en-IN')}</h2>
            </div>

            <div className="calc-details-grid">
              <div className="calc-detail-box">
                <span className="detail-label">Principal Amount</span>
                <span className="detail-val">₹ {amount.toLocaleString('en-IN')}</span>
              </div>
              <div className="calc-detail-box">
                <span className="detail-label">Total Interest Payable</span>
                <span className="detail-val" style={{ color: '#f59e0b' }}>
                  ₹ {Math.round(calcResult.totalInterest).toLocaleString('en-IN')}
                </span>
              </div>
              <div className="calc-detail-box">
                <span className="detail-label">Total Amount Payable</span>
                <span className="detail-val" style={{ color: '#38bdf8' }}>
                  ₹ {Math.round(calcResult.totalRepayment).toLocaleString('en-IN')}
                </span>
              </div>
              <div className="calc-detail-box">
                <span className="detail-label">Effective APR (incl. fee)</span>
                <span className="detail-val">{calcResult.apr.toFixed(2)}%</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Amortization Schedule Table */}
      {calcResult && calcResult.schedule && (
        <div className="glass-card" style={{ marginTop: '1.5rem' }}>
          <h3>Amortization Schedule (First 12 Months)</h3>
          <div className="table-responsive">
            <table className="comparison-table">
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Installment (EMI)</th>
                  <th>Principal Paid</th>
                  <th>Interest Paid</th>
                  <th>Remaining Balance</th>
                </tr>
              </thead>
              <tbody>
                {calcResult.schedule.slice(0, 12).map((item) => (
                  <tr key={item.month}>
                    <td>Month {item.month}</td>
                    <td>₹ {Math.round(item.installment).toLocaleString('en-IN')}</td>
                    <td style={{ color: '#10b981' }}>₹ {Math.round(item.principal).toLocaleString('en-IN')}</td>
                    <td style={{ color: '#f59e0b' }}>₹ {Math.round(item.interest).toLocaleString('en-IN')}</td>
                    <td>₹ {Math.round(item.balance).toLocaleString('en-IN')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
