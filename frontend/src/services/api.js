import axios from 'axios';

// Dynamically determine the backend base URL from environment variables with Render fallback
const getApiBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'https://finewise-ai-we0m.onrender.com';
  let cleanUrl = envUrl.trim().replace(/\/+$/, '');
  // If user provided a URL ending in /api, strip it so paths starting with /api/ don't become /api/api/
  if (cleanUrl.endsWith('/api')) {
    cleanUrl = cleanUrl.slice(0, -4);
  }
  return cleanUrl;
};

const API_BASE_URL = getApiBaseUrl();

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

export const api = {
  // 1. Health check
  async getHealth() {
    const response = await apiClient.get('/api/health');
    return response.data;
  },

  // 2. Upload files
  async uploadFiles(files) {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    const response = await apiClient.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  // 3. Get list of documents
  async getDocuments() {
    const response = await apiClient.get('/api/documents');
    return response.data;
  },

  // 4. Get document details (Extracted data + Clauses + 7-Component Risk Analysis + OCR Warnings)
  async getDocumentDetails(docId) {
    const response = await apiClient.get(`/api/documents/${docId}`);
    return response.data;
  },

  // 5. Re-analyze document
  async reanalyzeDocument(docId) {
    const response = await apiClient.post(`/api/documents/${docId}/analyze`);
    return response.data;
  },

  // 6. Financial Calculations & Amortization
  async getCalculations(docId) {
    const response = await apiClient.get(`/api/calculate/${docId}`);
    return response.data;
  },

  // 7. Clauses & Risk Details
  async getClauses(docId) {
    const response = await apiClient.get(`/api/documents/${docId}/risk`);
    return response.data;
  },

  // 8. Compare Multiple Loans
  async compareLoans(docIds = []) {
    const response = await apiClient.post('/api/compare', { doc_ids: docIds });
    return response.data;
  },

  // 9. RAG Chat Assistant
  async sendChatMessage(query, docIds = null) {
    const response = await apiClient.post('/api/chat', { query, doc_ids: docIds });
    return response.data;
  },

  // 10. ML Model Evaluation Metrics (Threshold sweep, Confusion matrix, ROC curves)
  async getMLEvaluation(threshold = 0.50) {
    const response = await apiClient.get('/api/ml/evaluation', { params: { threshold } });
    return response.data;
  },

  // 11. Predict Risk with ML
  async predictRiskML(data) {
    const response = await apiClient.post('/api/ml/predict', data);
    return response.data;
  },

  // 12. Load Pre-built Sample Docs
  async loadSampleDocs() {
    const response = await apiClient.post('/api/load-samples');
    return response.data;
  },

  // 13. PDF Report URL
  getReportPdfUrl(docId) {
    const base = API_BASE_URL || '';
    return `${base}/api/report/${docId}/pdf`;
  }
};

