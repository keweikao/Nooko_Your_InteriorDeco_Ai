import React, { useState, useRef } from 'react';
import './FileUpload.css';

function FileUpload({ projectId, apiBaseUrl, onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setUploadStatus('');
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files?.[0];
    if (file && ['application/pdf', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel', 'image/jpeg', 'image/png'].includes(file.type)) {
      setSelectedFile(file);
      setUploadStatus('');
    } else {
      setUploadStatus('請上傳有效的檔案格式（PDF、Excel 或圖片）');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('請先選擇一個檔案。');
      return;
    }
    if (!projectId) {
      setUploadStatus('專案 ID 尚未準備好。');
      return;
    }

    setUploadStatus('上傳中...');
    setUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${apiBaseUrl}/projects/${projectId}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setUploadStatus(`✓ ${data.message}`);
        setUploadProgress(100);
        setSelectedFile(null);

        if (onUploadSuccess) {
          setTimeout(() => {
            onUploadSuccess();
          }, 1500);
        }
      } else {
        const errorData = await response.json();
        setUploadStatus(`上傳失敗: ${errorData.detail || response.statusText}`);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadStatus('上傳失敗: 無法連接服務。');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <div
        className={`file-upload-zone ${dragActive ? 'active' : ''} ${selectedFile ? 'selected' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileChange}
          accept=".pdf,.xlsx,.xls,.jpg,.jpeg,.png"
          style={{ display: 'none' }}
        />

        <div className="upload-icon">
          {selectedFile ? '✓' : '📁'}
        </div>

        <div className="upload-text">
          {selectedFile ? (
            <>
              <p className="file-name">{selectedFile.name}</p>
              <p className="file-size">({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)</p>
            </>
          ) : (
            <>
              <p className="main-text">拖拽報價單到此處</p>
              <p className="sub-text">或點擊選擇檔案</p>
              <p className="format-hint">支援 PDF、Excel 或圖片格式</p>
            </>
          )}
        </div>
      </div>

      {uploading && (
        <div className="progress-container">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
          </div>
          <p className="progress-text">上傳中... {uploadProgress}%</p>
        </div>
      )}

      <div className="upload-actions">
        <button
          className={`upload-button ${uploading ? 'loading' : ''}`}
          onClick={handleUpload}
          disabled={!selectedFile || !projectId || uploading}
        >
          {uploading ? (
            <>
              <span className="loading-spinner"></span>
              上傳中...
            </>
          ) : (
            '上傳報價單 →'
          )}
        </button>
      </div>

      {uploadStatus && (
        <div className={`upload-status ${uploadStatus.includes('失敗') ? 'error' : 'success'}`}>
          {uploadStatus}
        </div>
      )}
    </div>
  );
}

export default FileUpload;