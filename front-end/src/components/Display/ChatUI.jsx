import React, { useEffect, useState } from 'react';
import './ChatUI.css';
import FileUploader from '../Upload/FileUploader';
import QuestionForm from '../Search/QuestionForm';
import PdfHistory from '../UserHistory/PdfHistory';

function ChatUI({ onLogout }) {
  const [selectedPdfId, setSelectedPdfId] = useState(null);
  const [selectedPdfTitle, setSelectedPdfTitle] = useState('');
  const [chatResetKey, setChatResetKey] = useState(0);
  const [pdfHistoryRefreshKey, setPdfHistoryRefreshKey] = useState(0);

  useEffect(() => {
    const savedId = localStorage.getItem('selectedPdfId');
    const savedTitle = localStorage.getItem('documentTitle');
    if (savedId) setSelectedPdfId(JSON.parse(savedId));
    if (savedTitle) setSelectedPdfTitle(JSON.parse(savedTitle));
  }, []);

  const handleDeleteChat = () => {
    localStorage.removeItem('selectedPdfId');
    localStorage.removeItem('documentTitle');
    setSelectedPdfId(null);
    setSelectedPdfTitle('');
    setChatResetKey((prevKey) => prevKey + 1);
  };

  const handleDocumentSelect = (id, title) => {
    setSelectedPdfId(id);
    setSelectedPdfTitle(title);
    localStorage.setItem('selectedPdfId', JSON.stringify(id));
    localStorage.setItem('documentTitle', JSON.stringify(title));
    setPdfHistoryRefreshKey((prevKey) => prevKey + 1);
  };

  return (
    <div className="display-part">
      <aside className="left-bar">
        <div className="new-chat" onClick={handleDeleteChat}>
          <span className="new-chat-icon">×</span>
          Delete Chat
        </div>
        <div className="history-panel">
          <h2>Uploaded Documents</h2>
          <PdfHistory selectedPdfId={selectedPdfId} onSelectDocument={handleDocumentSelect} refreshKey={pdfHistoryRefreshKey} />
        </div>
        <button className="logout-btn" onClick={onLogout} style={{ marginTop: 'auto', marginBottom: '10px' }}>
          Logout
        </button>
      </aside>

      <main className="main-bar">
        <header className="page-header">
          <div>
            <p className="subtitle">Ask questions based on uploaded PDF, image, or text</p>
            <h1>Document Chat Assistant</h1>
          </div>
          <div className="selected-document-chip">
            <span>Current document</span>
            <strong>{selectedPdfTitle || 'None selected'}</strong>
          </div>
        </header>

        <section className="upload-sections">
          <FileUploader onUploadSuccess={handleDocumentSelect} />
        </section>

        <section className="chat-section">
          <QuestionForm
            selectedPdfId={selectedPdfId}
            selectedPdfTitle={selectedPdfTitle}
            resetKey={chatResetKey}
          />
        </section>
      </main>
    </div>
  );
}

export default ChatUI;
