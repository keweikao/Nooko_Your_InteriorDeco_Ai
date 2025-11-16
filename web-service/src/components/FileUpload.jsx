import React, { useState } from 'react';

function FileUpload({ projectId, apiBaseUrl, onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setUploadStatus('');
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

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${apiBaseUrl}/api/projects/${projectId}/upload`, {
        method: 'POST',
        body: formData,
        // Note: Do NOT set Content-Type header for FormData, browser sets it automatically
      });

      if (response.ok) {
        const data = await response.json();
        setUploadStatus(`✓ ${data.message}`);
        setSelectedFile(null); // Clear selected file after successful upload

        // Call the success callback
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
    <div style={{ marginTop: '20px', paddingTop: '20px' }}>
      <div style={{
        border: '2px dashed #ccc',
        borderRadius: '8px',
        padding: '30px',
        textAlign: 'center',
        backgroundColor: '#f9f9f9'
      }}>
        <input
          type="file"
          onChange={handleFileChange}
          accept=".pdf,.xlsx,.xls,.jpg,.jpeg,.png"
          style={{ marginBottom: '15px' }}
        />
        <br />
        <button
          onClick={handleUpload}
          disabled={!selectedFile || !projectId || uploading}
          style={{
            padding: '12px 24px',
            backgroundColor: (!selectedFile || !projectId || uploading) ? '#ccc' : '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: (!selectedFile || !projectId || uploading) ? 'not-allowed' : 'pointer',
            fontSize: '16px'
          }}
        >
          {uploading ? '上傳中...' : '上傳報價單'}
        </button>
        {uploadStatus && (
          <p style={{
            marginTop: '15px',
            color: uploadStatus.includes('失敗') ? '#d32f2f' : '#4CAF50',
            fontWeight: '500'
          }}>
            {uploadStatus}
          </p>
        )}
      </div>
    </div>
  );
}

export default FileUpload;