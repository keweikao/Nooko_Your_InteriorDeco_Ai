import React, { useState, useRef, useEffect } from 'react';
import '../ConversationUI.css';

/**
 * 消息輸入框組件
 * 支持：
 * - 自動擴展文本框高度
 * - Shift+Enter 換行，Enter 發送
 * - 發送禁用狀態
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
    // IME 輸入時 (e.isComposing) 不要攔截 Enter，避免中文還未選字就送出
    if (e.isComposing) return;
    // Shift+Enter: 換行，Enter: 發送
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
