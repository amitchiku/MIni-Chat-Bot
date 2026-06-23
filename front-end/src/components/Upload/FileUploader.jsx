import React, { useState, useRef } from 'react';
import axios from 'axios';
import './FileUploader.css';

function FileUploader({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [title, setTitle] = useState('');
  const [textContent, setTextContent] = useState('');
  const fileInputRef = useRef(null);

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      setSelectedFile(file);
      setTitle(file.name);
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setTitle(file.name);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile && !textContent.trim()) {
      alert('Please upload a file or enter text before submitting.');
      return;
    }

    const formData = new FormData();
    if (selectedFile) {
      formData.append('file', selectedFile);
    }
    formData.append('title', title || (selectedFile ? selectedFile.name : 'Untitled Document'));
    if (textContent.trim()) {
      formData.append('text', textContent.trim());
    }

    try {
      const response = await axios.post('http://localhost:8000/upload-pdf/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      onUploadSuccess(response.data.id, response.data.title);
      setSelectedFile(null);
      setTextContent('');
      setTitle(response.data.title || '');
    } catch (error) {
      console.error(error);
      alert(error.response?.data?.message || 'Upload failed.');
    }
  };

  return (
    <div className="file-uploader">
      <div className="upload-card">
        <h3>Upload PDF or Image</h3>
        <div
          className="file-drop-area"
          onDrop={handleDrop}
          onDragOver={(event) => event.preventDefault()}
          onClick={() => fileInputRef.current.click()}
        >
          {selectedFile ? selectedFile.name : 'Click or drop PDF, TXT, PNG, JPG, JPEG, BMP, GIF'}
        </div>
        <input
          type="file"
          accept=".pdf,.txt,image/*"
          onChange={handleFileChange}
          style={{ display: 'none' }}
          ref={fileInputRef}
        />
      </div>

      <div className="upload-card">
        <h3>Paste Text</h3>
        <textarea
          className="text-input"
          placeholder="Paste your text here when you do not want to upload a file"
          value={textContent}
          onChange={(e) => setTextContent(e.target.value)}
          rows={7}
        />
      </div>

      <div className="upload-actions">
        <input
          type="text"
          className="title-input"
          placeholder="Document title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <button className="upload-btn" onClick={handleUpload}>Upload Document</button>
      </div>
    </div>
  );
}

export default FileUploader;
