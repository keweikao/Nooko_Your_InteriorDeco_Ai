import React from 'react';
import '../ConversationUI.css';

/**
 * Agent 正在輸入的動畫指示器
 */
function TypingIndicator() {
  return (
    <div className="typing-indicator-container">
      <div className="typing-indicator">
        <span className="typing-dot"></span>
        <span className="typing-dot"></span>
        <span className="typing-dot"></span>
      </div>
      <p className="typing-text">施工主任正在思考...</p>
    </div>
  );
}

export default TypingIndicator;
