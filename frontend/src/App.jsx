import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DocumentUpload from './components/DocumentUpload';
import Dashboard from './components/Dashboard';
import ComparisonView from './components/ComparisonView';
import RAGChatAssistant from './components/RAGChatAssistant';
import FinancialCalculator from './components/FinancialCalculator';
import MLEvaluationView from './components/MLEvaluationView';
import { api } from './services/api';
import './App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [documents, setDocuments] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState(null);
  const [docDetail, setDocDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingSamples, setLoadingSamples] = useState(false);

  useEffect(() => {
    fetchDocuments(true);
  }, []);

  useEffect(() => {
    if (selectedDocId) {
      fetchDocDetail(selectedDocId);
    }
  }, [selectedDocId]);

  const fetchDocuments = async (autoLoadSampleIfEmpty = false) => {
    try {
      const docs = await api.getDocuments();
      setDocuments(docs);
      if (docs.length > 0) {
        if (!selectedDocId) setSelectedDocId(docs[0].id);
      } else if (autoLoadSampleIfEmpty) {
        handleLoadSamples();
      }
    } catch (err) {
      console.error('Error fetching documents:', err);
    }
  };

  const fetchDocDetail = async (id) => {
    setLoading(true);
    try {
      const detail = await api.getDocumentDetails(id);
      setDocDetail(detail);
    } catch (err) {
      console.error('Error fetching document details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (files) => {
    const newDocs = await api.uploadFiles(files);
    await fetchDocuments();
    if (newDocs && newDocs.length > 0) {
      setSelectedDocId(newDocs[0].id);
      setActiveTab('dashboard');
    }
  };

  const handleLoadSamples = async () => {
    setLoadingSamples(true);
    try {
      await api.loadSampleDocs();
      const docs = await api.getDocuments();
      setDocuments(docs);
      if (docs.length > 0) {
        setSelectedDocId(docs[0].id);
      }
    } catch (err) {
      console.error('Error loading sample documents:', err);
    } finally {
      setLoadingSamples(false);
    }
  };

  return (
    <div className="app-wrapper">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        docCount={documents.length}
        onLoadSamples={handleLoadSamples}
        loadingSamples={loadingSamples}
      />

      <main className="main-content">
        {activeTab === 'dashboard' && (
          <Dashboard
            docDetail={docDetail}
            selectedDocId={selectedDocId}
            documents={documents}
            onSelectDoc={(id) => setSelectedDocId(id)}
          />
        )}

        {activeTab === 'upload' && (
          <DocumentUpload
            documents={documents}
            onUpload={handleUpload}
            onSelectDoc={(id) => { setSelectedDocId(id); setActiveTab('dashboard'); }}
            selectedDocId={selectedDocId}
            onLoadSamples={handleLoadSamples}
            loading={loadingSamples}
          />
        )}

        {activeTab === 'compare' && (
          <ComparisonView
            documents={documents}
            onSelectDoc={(id) => { setSelectedDocId(id); setActiveTab('dashboard'); }}
          />
        )}

        {activeTab === 'chat' && (
          <RAGChatAssistant
            documents={documents}
            selectedDocId={selectedDocId}
          />
        )}

        {activeTab === 'calculator' && (
          <FinancialCalculator
            docDetail={docDetail}
          />
        )}

        {activeTab === 'ml-eval' && (
          <MLEvaluationView />
        )}
      </main>
    </div>
  );
}
