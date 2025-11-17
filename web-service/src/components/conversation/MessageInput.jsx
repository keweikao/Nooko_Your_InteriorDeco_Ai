import React, { useState, useRef, useEffect } from 'react';
import '../ConversationUI.css';

/**
 * 消息輸入框組件
 * Input source: 使用者輸入文字
 * Output: 呼叫 onSend(message)，由 Conversation UI 將文字送往後端 SSE
 * Behavior: 自動調整高度、支援 IME（Enter 只確認文字，不送出）、Shift+Enter 換行
 */
function MessageInput({ onSend, disabled = false, isLoading = false }) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  // 自動調整文本框高度
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleKeyDown = (e) => {
    // IME 輸入中 (e.isComposing) 時，Enter 只用於確認選字，不做送出
    if (e.isComposing) return;
    // Shift+Enter: 換行；單獨 Enter：送出訊息
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    const message = input.trim();
    if (message && !disabled && !isLoading) {
      onSend(message);
      setInput('');
      // 重置文本框高度
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  return (
    <div className="message-input-container">
      <div className="message-input-wrapper">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="輸入您的消息... (Shift+Enter 換行)"
          disabled={disabled || isLoading}
          className="message-input"
          rows="1"
        />

        <button
          onClick={handleSend}
          disabled={!input.trim() || disabled || isLoading}
          className="message-send-button"
          title={disabled ? '等待 Agent 回應' : '發送消息 (Enter)'}
        >
          {isLoading ? (
            <span className="send-spinner">⏳</span>
          ) : (
            <span className="send-icon">➤</span>
          )}
        </button>
      </div>

      <div className="input-footer">
        <p className="input-hint">
          您的對話已加密並安全存儲
        </p>
      </div>
    </div>
  );
}

export default MessageInput;
