import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './PdfHistory.css';

function PdfHistory({ selectedPdfId, onSelectDocument, refreshKey }) {
  const [pdfHistory, setPDFHistory] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/pdf-history/')
      .then((response) => {
        setPDFHistory(response.data);
      })
      .catch((error) => {
        console.error('Error fetching PDF history:', error);
      });
  }, [refreshKey]);

  const handlePDFClick = (pdf) => {
    onSelectDocument(pdf.id, pdf.title);
  };

  return (
    <div className="pdfhistory">
      {pdfHistory.length === 0 && <p className="empty-history">No documents uploaded yet.</p>}
      {pdfHistory.map((entry) => (
        <button
          key={entry.id}
          type="button"
          onClick={() => handlePDFClick(entry)}
          className={`eachPdf ${selectedPdfId === entry.id ? 'selected' : ''}`}
        >
          <span>{entry.title}</span>
          <small>{new Date(entry.upload_date).toLocaleString()}</small>
        </button>
      ))}
    </div>
  );
}

export default PdfHistory;
