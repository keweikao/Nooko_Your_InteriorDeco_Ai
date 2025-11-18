import React, { useState, useEffect } from 'react';

const AnalysisSection = ({ projectId, apiBaseUrl }) => {
  const [messages, setMessages] = useState([]);
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const [loadingMessages, setLoadingMessages] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMessages = async () => {
      try {
        setLoadingMessages(true);
        const response = await fetch(`${apiBaseUrl}/projects/${projectId}/analysis-messages`);
        if (!response.ok) {
          throw new Error('Failed to fetch analysis messages');
        }
        const data = await response.json();
        setMessages(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoadingMessages(false);
      }
    };

    if (projectId) {
      fetchMessages();
    }
  }, [projectId, apiBaseUrl]);

  useEffect(() => {
    if (messages.length > 0) {
      const interval = setInterval(() => {
        setCurrentMessageIndex((prevIndex) => (prevIndex + 1) % messages.length);
      }, 3000); // Change message every 3 seconds
      return () => clearInterval(interval);
    }
  }, [messages]);

  if (loadingMessages) {
    return (
      <div className="analysis-section flex flex-col items-center justify-center p-6 bg-nooko-white rounded-lg shadow-lg text-nooko-charcoal min-h-[300px]">
        <svg className="animate-spin h-10 w-10 text-nooko-terracotta" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p className="mt-4 text-lg font-playfair font-bold">AI 智慧分析中...</p>
        <p className="text-sm text-gray-600 mt-2">正在載入分析訊息...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analysis-section flex flex-col items-center justify-center p-6 bg-nooko-white rounded-lg shadow-lg text-nooko-charcoal min-h-[300px]">
        <p className="text-red-500 text-lg">錯誤: {error}</p>
      </div>
    );
  }

  return (
    <div className="analysis-section flex flex-col items-center justify-center p-6 bg-nooko-white rounded-lg shadow-lg text-nooko-charcoal min-h-[300px]">
      <svg className="animate-spin h-10 w-10 text-nooko-terracotta" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p className="mt-4 text-lg font-playfair font-bold">AI 智慧分析中...</p>
      {messages.length > 0 && (
        <p className="text-sm text-gray-600 mt-2 text-center transition-opacity duration-500 ease-in-out">
          {messages[currentMessageIndex]}
        </p>
      )}
    </div>
  );
};

export default AnalysisSection;
