import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export const api = {
  // 1. Health check
  async getHealth() {
    const response = await axios.get(`${API_BASE}/health`);
    return response.data;
  },

  // 2. Upload files
  async uploadFiles(files) {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    const response = await axios.post(`${API_BASE}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  // 3. Get list of documents
  async getDocuments() {
    const response = await axios.get(`${API_BASE}/documents`);
    return response.data;
  },

  // 4. Get document details (Extracted data + Clauses + 7-Component Risk Analysis + OCR Warnings)
  async getDocumentDetails(docId) {
    const response = await axios.get(`${API_BASE}/documents/${docId}`);
    return response.data;
  },

  // 5. Re-analyze document
  async reanalyzeDocument(docId) {
    const response = await axios.post(`${API_BASE}/documents/${docId}/analyze`);
    return response.data;
  },

  // 6. Financial Calculations & Amortization
  async getCalculations(docId) {
    const response = await axios.get(`${API_BASE}/calculate/${docId}`);
    return response.data;
  },

  // 7. Clauses & Risk Details
  async getClauses(docId) {
    const response = await axios.get(`${API_BASE}/documents/${docId}/risk`);
    return response.data;
  },

  // 8. Compare Multiple Loans
  async compareLoans(docIds = []) {
    const response = await axios.post(`${API_BASE}/compare`, { doc_ids: docIds });
    return response.data;
  },

  // 9. RAG Chat Assistant
  async sendChatMessage(query, docIds = null) {
    const response = await axios.post(`${API_BASE}/chat`, { query, doc_ids: docIds });
    return response.data;
  },

  // 10. ML Model Evaluation Metrics (Threshold sweep, Confusion matrix, ROC curves)
  async getMLEvaluation(threshold = 0.50) {
    const response = await axios.get(`${API_BASE}/ml/evaluation`, { params: { threshold } });
    return response.data;
  },

  // 11. Predict Risk with ML
  async predictRiskML(data) {
    const response = await axios.post(`${API_BASE}/ml/predict`, data);
    return response.data;
  },

  // 12. Load Pre-built Sample Docs
  async loadSampleDocs() {
    const response = await axios.post(`${API_BASE}/load-samples`);
    return response.data;
  },

  // 13. PDF Report URL
  getReportPdfUrl(docId) {
    return `${API_BASE}/report/${docId}/pdf`;
  }
};
