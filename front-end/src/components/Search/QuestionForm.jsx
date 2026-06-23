import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './QuestionForm.css';

function QuestionForm({ selectedPdfId, selectedPdfTitle, resetKey }) {
  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState([]);

  useEffect(() => {
    setHistory([]);
    setQuestion('');
  }, [resetKey]);

  const handleQuestionSubmit = async () => {
    if (!question.trim()) {
      return;
    }

    try {
      const response = await axios.post('http://localhost:8000/ask-question/', {
        question: question.trim(),
        pdfId: selectedPdfId,
      });

      const newEntry = {
        question: question.trim(),
        answer: response.data.answer,
      };
      setHistory((prevHistory) => [newEntry, ...prevHistory]);
      setQuestion('');
    } catch (error) {
      console.error('Error submitting question:', error.response?.data || error.message);
      alert(error.response?.data?.message || 'Failed to submit question.');
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleQuestionSubmit();
    }
  };

  return (
    <div className='main'>
      <div className='question-header'>
        <div>
          <h2>Ask a question</h2>
          <p className='document-label'>
            Selected document: <strong>{selectedPdfTitle || 'None selected'}</strong>
          </p>
          {!selectedPdfId && (
            <p className='note'>You can still ask a question; the latest uploaded document will be used if none is selected.</p>
          )}
        </div>
      </div>

      <div className="searchbar">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your question here and press Ask"
          className='question-box'
          rows={5}
        />
        <button className='ask-btn' onClick={handleQuestionSubmit} disabled={!question.trim()}>
          Ask
        </button>
      </div>

      <div className='history'>
        {history.length === 0 && <p className='empty-history'>No Q&A yet. Ask a question to see the result here.</p>}
        {history.map((entry, index) => (
          <div key={index} className='history-entry'>
            <p className='question'><span>Q:</span> {entry.question}</p>
            <p className='answer'><span>A:</span> {entry.answer}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default QuestionForm;
