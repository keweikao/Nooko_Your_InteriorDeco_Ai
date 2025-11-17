import React, { useEffect, useState } from 'react';
import '../ConversationUI.css';

/**
 * 單條消息組件
 * 支持不同發送者 (user/agent) 的樣式差異
 * 支持流式渲染 (逐字顯示)
 */
function MessageItem({ message, isStreaming = false }) {
  const [displayText, setDisplayText] = useState('');
  const isAgent = message.sender === 'agent';

  useEffect(() => {
    if (isStreaming) {
      // 流式顯示文本 - 逐字動畫
      let currentIndex = 0;
      const interval = setInterval(() => {
        if (currentIndex < message.content.length) {
          setDisplayText(message.content.substring(0, currentIndex + 1));
          currentIndex++;
        } else {
          clearInterval(interval);
        }
      }, 20); // 每 20ms 顯示一個字符

      return () => clearInterval(interval);
    } else {
      setDisplayText(message.content);
    }
  }, [message.content, isStreaming]);

  return (
    <div className={`message-item ${isAgent ? 'agent-message' : 'user-message'}`}>
      {isAgent && (
        <div className="relative message-avatar">
          <img src="https://placehold.co/40x40/EBF0F4/7C8490?text=A&font=sans" alt="Agent Avatar" className="avatar-circle" />
          <span className="absolute bottom-0 right-0 block w-3 h-3 bg-green-500 border-2 border-white rounded-full"></span>
        </div>
      )}

      <div className="message-content-wrapper">
        <div className={`message-bubble ${isAgent ? 'agent-bubble' : 'user-bubble'}`}>
          <p className="message-text">{displayText}</p>
          {isStreaming && <span className="message-cursor">▌</span>}
        </div>
        <span className="message-timestamp">
          {new Date(message.timestamp).toLocaleTimeString('zh-TW', {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </span>
      </div>

      {!isAgent && message.status !== 'sent' && (
        <span className="message-status">
          {message.status === 'sending' && '⏱️'}
          {message.status === 'error' && '❌'}
        </span>
      )}
    </div>
  );
}

export default MessageItem;
