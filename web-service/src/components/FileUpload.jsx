import React, { useState, useRef } from 'react';
// import './FileUpload.css'; // Removed custom CSS import

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
      const response = await fetch(`${apiBaseUrl}/api/projects/${projectId}/upload`, {
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
    <div className="flex flex-col items-center justify-center p-6 bg-nooko-white rounded-lg shadow-lg">
      <div
        className={`flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer transition-all duration-300 ease-in-out
          ${dragActive ? 'border-nooko-terracotta bg-nooko-terracotta/10' : 'border-gray-300 hover:border-nooko-terracotta hover:bg-gray-50'}
          ${selectedFile ? 'border-nooko-terracotta bg-nooko-terracotta/10' : ''}`}
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
          className="hidden"
        />

        <div className="text-5xl text-gray-400 mb-4">
          {selectedFile ? '✅' : '📁'}
        </div>

        <div className="text-center">
          {selectedFile ? (
            <>
              <p className="text-lg font-semibold text-nooko-charcoal">{selectedFile.name}</p>
              <p className="text-sm text-gray-500">({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)</p>
            </>
          ) : (
            <>
              <p className="text-lg font-semibold text-nooko-charcoal">拖拽報價單到此處</p>
              <p className="text-sm text-gray-500 mt-1">或點擊選擇檔案</p>
              <p className="text-xs text-gray-400 mt-2">支援 PDF、Excel 或圖片格式</p>
            </>
          )}
        </div>
      </div>

      {uploading && (
        <div className="w-full mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div className="bg-nooko-terracotta h-2.5 rounded-full" style={{ width: `${uploadProgress}%` }}></div>
          </div>
          <p className="text-sm text-gray-500 mt-2 text-center">上傳中... {uploadProgress}%</p>
        </div>
      )}

      <div className="w-full mt-6">
        <button
          className={`w-full px-6 py-3 rounded-lg font-bold text-nooko-white transition-all duration-300 ease-in-out
            ${!selectedFile || !projectId || uploading ? 'bg-gray-400 cursor-not-allowed' : 'bg-nooko-terracotta hover:bg-nooko-terracotta/90 shadow-md'}`}
          onClick={handleUpload}
          disabled={!selectedFile || !projectId || uploading}
        >
          {uploading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              上傳中...
            </span>
          ) : (
            '上傳報價單 →'
          )}
        </button>
      </div>

      {uploadStatus && (
        <div className={`mt-4 text-center text-sm ${uploadStatus.includes('失敗') ? 'text-red-500' : 'text-green-600'}`}>
          {uploadStatus}
        </div>
      )}

      <p className="text-xs text-gray-500 mt-4 text-center">
        <span className="font-bold">隱私承諾:</span> 您的文件僅用於本次分析，全程加密，我們絕不分享或用於其他目的。
      </p>
    </div>
  );
}

export default FileUpload;