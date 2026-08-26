import React from 'react';
import { ShieldCheck, UploadCloud, LayoutDashboard, GitCompare, MessageSquare, Calculator, Cpu, Sparkles } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, docCount, onLoadSamples, loadingSamples }) {
  return (
    <header className="navbar-container">
      <div className="nav-inner">
        {/* Brand Logo */}
        <div className="brand-logo" onClick={() => setActiveTab('dashboard')} style={{ cursor: 'pointer' }}>
          <div className="logo-icon-bg">
            <ShieldCheck size={26} color="#38bdf8" />
          </div>
          <div>
            <div className="brand-title">
              FinWise <span className="gradient-text">AI</span>
            </div>
            <div className="brand-subtitle">Financial Decision Support</div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="nav-tabs">
          <button
            id="tab-dashboard"
            className={`nav-tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={18} />
            <span>Dashboard</span>
          </button>

          <button
            id="tab-upload"
            className={`nav-tab-btn ${activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            <UploadCloud size={18} />
            <span>Documents ({docCount})</span>
          </button>

          <button
            id="tab-compare"
            className={`nav-tab-btn ${activeTab === 'compare' ? 'active' : ''}`}
            onClick={() => setActiveTab('compare')}
          >
            <GitCompare size={18} />
            <span>Loan Comparison</span>
          </button>

          <button
            id="tab-chat"
            className={`nav-tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            <MessageSquare size={18} />
            <span>AI Copilot</span>
          </button>

          <button
            id="tab-calculator"
            className={`nav-tab-btn ${activeTab === 'calculator' ? 'active' : ''}`}
            onClick={() => setActiveTab('calculator')}
          >
            <Calculator size={18} />
            <span>Calculator</span>
          </button>

          <button
            id="tab-ml-eval"
            className={`nav-tab-btn ${activeTab === 'ml-eval' ? 'active' : ''}`}
            onClick={() => setActiveTab('ml-eval')}
          >
            <Cpu size={18} />
            <span>ML Evaluation</span>
          </button>
        </nav>

        {/* Quick Sample Loader Button */}
        <div className="nav-actions">
          <button
            id="btn-load-samples"
            className="btn btn-outline"
            onClick={onLoadSamples}
            disabled={loadingSamples}
          >
            <Sparkles size={16} />
            <span>{loadingSamples ? 'Loading...' : 'Load Sample Docs'}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
