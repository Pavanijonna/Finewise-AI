import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, FileCheck, ArrowRight, Sparkles } from 'lucide-react';

export default function DocumentUpload({ documents, onUpload, onSelectDoc, selectedDocId, onLoadSamples, loading }) {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await processFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = async (e) => {
    if (e.target.files && e.target.files[0]) {
      await processFiles(e.target.files);
    }
  };

  const processFiles = async (files) => {
    setUploading(true);
    setErrorMsg(null);
    try {
      await onUpload(files);
    } catch (err) {
      setErrorMsg('Failed to upload and process documents. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-container animate-fade-in">
      <div className="section-header">
        <h2>Document Management & <span className="gradient-text">OCR Processing</span></h2>
        <p className="subtitle">Upload loan agreements, sanction letters, or financial PDF/Image documents for automated NLP extraction.</p>
      </div>

      {/* Drag and Drop Zone */}
      <div
        className={`dropzone-card ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          id="file-upload-input"
          type="file"
          multiple
          accept=".pdf,.png,.jpg,.jpeg,.txt"
          onChange={handleFileInput}
          style={{ display: 'none' }}
        />
        
        <div className="dropzone-content">
          <div className="upload-icon-wrapper">
            <Upload size={36} color="#38bdf8" />
          </div>

          <h3>Drag & Drop Financial Contracts</h3>
          <p className="upload-hint">Supports PDF, PNG, JPG, or TXT (Multiple files allowed)</p>

          <div className="upload-button-group">
            <label htmlFor="file-upload-input" className="btn btn-primary" id="btn-browse-files">
              <FileCheck size={18} />
              <span>{uploading ? 'Processing OCR...' : 'Select Files'}</span>
            </label>

            <button
              id="btn-sample-trigger"
              type="button"
              className="btn btn-secondary"
              onClick={onLoadSamples}
              disabled={loading}
            >
              <Sparkles size={18} color="#a855f7" />
              <span>Load 3 Demo Loans</span>
            </button>
          </div>
        </div>
      </div>

      {errorMsg && (
        <div className="error-alert">
          <AlertCircle size={18} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Uploaded Documents List */}
      <div className="docs-list-section">
        <h3>Uploaded Contracts ({documents.length})</h3>

        {documents.length === 0 ? (
          <div className="empty-state glass-card">
            <FileText size={40} color="#64748b" />
            <p>No documents uploaded yet. Click <strong>"Load 3 Demo Loans"</strong> above for instant exploration!</p>
          </div>
        ) : (
          <div className="grid-3">
            {documents.map((doc) => {
              const isSelected = doc.id === selectedDocId;
              return (
                <div
                  key={doc.id}
                  id={`doc-card-${doc.id}`}
                  className={`doc-card glass-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => onSelectDoc(doc.id)}
                >
                  <div className="doc-card-header">
                    <div className="doc-type-badge">{doc.file_type}</div>
                    <span className="doc-status"><CheckCircle size={14} color="#10b981" /> Ready</span>
                  </div>

                  <h4 className="doc-filename">{doc.filename}</h4>

                  <p className="doc-snippet">
                    {doc.text_snippet ? doc.text_snippet : 'OCR text extracted and normalized.'}
                  </p>

                  <div className="doc-card-footer">
                    <span className="doc-id">ID: {doc.id}</span>
                    <button className="btn-icon">
                      <span>Analyze</span>
                      <ArrowRight size={16} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
