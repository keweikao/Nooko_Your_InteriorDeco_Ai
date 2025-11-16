import React from 'react';
import '../ConversationUI.css';

/**
 * Agent 卡片組件
 * 顯示 Agent 的頭像、名稱、狀態
 */
function AgentCard({ agent }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'idle':
        return 'status-idle';
      case 'typing':
        return 'status-typing';
      case 'analyzing':
        return 'status-analyzing';
      default:
        return 'status-idle';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'idle':
        return '待命中';
      case 'typing':
        return '正在輸入...';
      case 'analyzing':
        return '分析中...';
      default:
        return '離線';
    }
  };

  return (
    <div className="agent-card">
      <div className="agent-header">
        <div className="agent-avatar-container">
          <img
            src={agent?.avatar || '🤖'}
            alt={agent?.name || 'Agent'}
            className="agent-avatar-image"
          />
          <span className={`agent-status-indicator ${getStatusColor(agent?.status)}`}></span>
        </div>

        <div className="agent-info">
          <h2 className="agent-name">{agent?.name || '施工主任'}</h2>
          <p className="agent-status-text">{getStatusText(agent?.status)}</p>
        </div>
      </div>

      <div className="agent-bio">
        <p>
          歡迎！我是您的專業施工主任。我會根據您上傳的報價單和裝修需求，
          為您提供專業的建議和分析。
        </p>
      </div>
    </div>
  );
}

export default AgentCard;
