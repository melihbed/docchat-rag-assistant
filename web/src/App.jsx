import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  // State for uploaded documents
  const [documents, setDocuments] = useState([]);
  // State for chat messages
  const [messages, setMessages] = useState([]);
  // State for the question input
  const [question, setQuestion] = useState("");
  // Loading states
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);

  // ─── Clear Handler ────────────────────────────────
  const clearDocuments = async () => {
    if (!window.confirm("Clear all documents and chat history?")) return;
    try {
      await axios.post("/api/clear");
      setDocuments([]);
      setMessages([]);
    } catch (err) {
      alert(err.response?.data?.detail || "Clear failed");
    }
  };
  // ─── Upload Handler ───────────────────────────────
  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    try {
      const res = await axios.post("/api/upload", formData);
      setDocuments((prev) => [...prev, res.data]);
    } catch (err) {
      alert(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
      e.target.value = ""; // reset file input
    }
  };

  // ─── Query Handler ────────────────────────────────
  const handleAsk = async () => {
    if (!question.trim()) return;

    // Add user message to chat
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setQuestion("");
    setAsking(true);

    try {
      const res = await axios.post("/api/query", null, {
        params: { query: question },
      });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: res.data.answer, sources: res.data.sources },
      ]);
    } catch (err) {
      alert(err.response?.data?.detail || "Query failed");
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="app">
      {/* Sidebar */}
      <div className="sidebar">
        <h2>DocChat</h2>

        {/* Upload */}
        <label className="upload-btn">
          {uploading ? "Uploading..." : "Upload PDF / DOCX"}
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleUpload}
            disabled={uploading}
            hidden
          />
        </label>
        <button
          className="clear-btn"
          onClick={clearDocuments}
          disabled={documents.length === 0}
        >
          🗑️ Clear All Documents
        </button>

        {/* Document List */}
        <div className="doc-list">
          <h3>Documents ({documents.length})</h3>
          {documents.length === 0 && <p className="empty">No documents yet</p>}
          {documents.map((doc) => (
            <div key={doc.doc_id} className="doc-card">
              <span className="doc-type">{doc.file_type}</span>
              <div>
                <div className="doc-name">{doc.filename}</div>
                <div className="doc-meta">{doc.chunks} chunks</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="chat">
        {/* Messages */}
        <div className="messages">
          {messages.length === 0 && (
            <div className="empty-chat">
              <p>Upload documents and ask questions</p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <div className="bubble">{msg.text}</div>
              {msg.sources && (
                <div className="sources">
                  {msg.sources.map((s, j) => (
                    <span key={j} className="source-tag">
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {asking && (
            <div className="message assistant">
              <div className="bubble">Thinking...</div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="input-area">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAsk()}
            placeholder="Ask about your documents..."
            disabled={asking}
          />
          <button onClick={handleAsk} disabled={asking || !question.trim()}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
