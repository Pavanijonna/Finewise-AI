import React, { useState } from 'react';
import { Send, Bot, User, Sparkles, BookOpen, ShieldAlert, CheckCircle2, AlertCircle, Info } from 'lucide-react';
import { api } from '../services/api';

export default function RAGChatAssistant({ documents, selectedDocId }) {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: "Hello! I am your FinWise AI Grounded RAG Copilot. Ask me questions about your uploaded financial contracts (e.g. 'What is the interest rate?', 'Can I close early?', 'What happens if payment is late?', 'Is there an insurance fee?').",
      sources: []
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const samplePrompts = [
    "What is the interest rate?",
    "What is the EMI?",
    "What happens if payment is late?",
    "Is foreclosure allowed?",
    "What fees are charged?",
    "What is the loan tenure?"
  ];

  const handleSend = async (queryText) => {
    const q = queryText || inputQuery;
    if (!q.trim()) return;

    const userMsg = { sender: 'user', text: q };
    setMessages(prev => [...prev, userMsg]);
    if (!queryText) setInputQuery('');
    setLoading(true);

    try {
      const docIds = selectedDocId ? [selectedDocId] : (documents.map(d => d.id));
      const response = await api.sendChatMessage(q, docIds);

      const botMsg = {
        sender: 'bot',
        text: response.answer,
        sources: response.sources || [],
        confidence: response.confidence_score,
        grounded: response.grounded,
        disclaimer: response.disclaimer
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          sender: 'bot',
          text: "I encountered an error retrieving document context. Please verify that a document has been uploaded.",
          sources: [],
          grounded: false
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container glass-card animate-fade-in" style={{ margin: '1rem 0' }}>
      <div className="chat-header">
        <div className="chat-title-group">
          <div className="logo-icon-bg" style={{ width: 36, height: 36 }}>
            <Bot size={20} color="#38bdf8" />
          </div>
          <div>
            <h3>Grounded RAG AI Copilot</h3>
            <span className="chat-status">
              <CheckCircle2 size={12} color="#10b981" /> Document-Grounded Generation with Verified Page Citations
            </span>
          </div>
        </div>

        {selectedDocId && (
          <span className="badge badge-medium">Active Doc Scoped</span>
        )}
      </div>

      {/* Suggested Prompts Pills */}
      <div className="suggested-prompts">
        <span className="suggested-label"><Sparkles size={14} color="#a855f7" /> Standard Benchmark Queries:</span>
        <div className="prompts-pills-list">
          {samplePrompts.map((p, idx) => (
            <button
              key={idx}
              className="prompt-pill"
              onClick={() => handleSend(p)}
              disabled={loading}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Messages Stream */}
      <div className="messages-box">
        {messages.map((m, idx) => (
          <div key={idx} className={`message-row ${m.sender === 'user' ? 'message-user' : 'message-bot'}`}>
            <div className="avatar">
              {m.sender === 'user' ? <User size={18} /> : <Bot size={18} color="#38bdf8" />}
            </div>
            <div className="message-content">
              <div className="message-text">{m.text}</div>

              {/* Source Snippets Citations with Page Numbers */}
              {m.sources && m.sources.length > 0 && (
                <div className="sources-citation" style={{ marginTop: '0.75rem' }}>
                  <div className="sources-title font-bold small-text flex-row items-center gap-2" style={{ color: '#38bdf8' }}>
                    <BookOpen size={14} /> Verified Contract Citations:
                  </div>
                  {m.sources.map((src, sIdx) => (
                    <div key={sIdx} className="source-item small-text" style={{ margin: '4px 0', padding: '6px', background: '#0f172a', borderRadius: '6px' }}>
                      <strong style={{ color: '#a855f7' }}>[{src.citation || `Source: ${src.filename}, Page: ${src.page_number}`}]:</strong> "{src.snippet}"
                    </div>
                  ))}
                </div>
              )}

              {m.disclaimer && (
                <div className="small-text text-muted" style={{ marginTop: '0.5rem', fontStyle: 'italic', fontSize: '0.75rem' }}>
                  {m.disclaimer}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message-row message-bot">
            <div className="avatar"><Bot size={18} color="#38bdf8" /></div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Chat Input Box */}
      <form
        onSubmit={(e) => { e.preventDefault(); handleSend(); }}
        className="chat-input-form"
      >
        <input
          id="chat-query-input"
          type="text"
          placeholder="Ask a question about your uploaded document clauses..."
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          className="input-field"
          disabled={loading}
        />
        <button
          id="btn-send-chat"
          type="submit"
          className="btn btn-primary"
          disabled={loading || !inputQuery.trim()}
        >
          <Send size={16} />
          <span>Ask</span>
        </button>
      </form>
    </div>
  );
}
