import React from 'react';
import AgentCard from './conversation/AgentCard';
import MessageList from './conversation/MessageList';
import MessageInput from './conversation/MessageInput';
import TypingIndicator from './conversation/TypingIndicator';
import ConversationProgress from './conversation/ConversationProgress';
import useConversation from '../hooks/useConversation';
import './ConversationUI.css';

/**
 * 主對話容器組件
 * 整合所有子組件，管理 Agent 和用戶的實時對話
 */
function ConversationUI({ projectId, apiBaseUrl, onConversationComplete }) {
  const {
    messages,
    agent,
    progress,
    missingFields,
    canComplete,
    loading,
    error,
    streamingMessageId,
    sendMessage,
    completeConversation
  } = useConversation(projectId, apiBaseUrl);

  const handleConversationEnd = async () => {
    const result = await completeConversation();
    if (result && onConversationComplete) {
      onConversationComplete(result);
    }
  };

  const isInputDisabled = loading || streamingMessageId !== null;
  console.log('ConversationUI - isInputDisabled:', isInputDisabled, 'loading:', loading, 'streamingMessageId:', streamingMessageId); // Added log

  if (loading && messages.length === 0) {
    return (
      <div className="conversation-loading">
        <div className="loading-spinner">
          <div className="spinner-ring"></div>
        </div>
        <p className="loading-text">初始化對話中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="conversation-error">
        <p className="error-icon">⚠️</p>
        <p className="error-message">{error}</p>
        <button className="error-retry-button">重試</button>
      </div>
    );
  }

  return (
    <div className="conversation-container">
      {/* 標題 */}
      <div className="conversation-header">
        <h1 className="conversation-title">Nooko 裝潢 AI 夥伴</h1>
        <p className="conversation-subtitle">與 HouseIQ 進行需求訪談</p>
      </div>

      {/* Agent 卡片 */}
      <AgentCard agent={agent} />

      {/* 進度指示 */}
      <ConversationProgress progress={progress} />

      {/* 待補資訊面板 */}
      {/* 顯示階段與缺失欄位的狀態面板 (input: SSE metadata, output: UI 中的待補列表) */}
      <div className="conversation-status-panel">
        <div className="conversation-status-left">
          <p className="conversation-stage-label">
            目前階段：<span>{progress.stage}</span>
          </p>
          <p className="conversation-stage-desc">{progress.description}</p>
        </div>
        <div className="conversation-status-right">
          <p className="missing-title">待補資訊（{missingFields.length}）</p>
          {missingFields.length === 0 ? (
            <p className="missing-empty">所有核心資訊已蒐集完成 🎉</p>
          ) : (
            <ul className="missing-list">
              {missingFields.slice(0, 4).map((item) => (
                <li key={item.id}>
                  <span className="missing-label">{item.label}</span>
                  <span className="missing-category">{item.category}</span>
                </li>
              ))}
              {missingFields.length > 4 && (
                <li className="missing-more">還有 {missingFields.length - 4} 項待補...</li>
              )}
            </ul>
          )}
        </div>
      </div>

      {/* 消息區域 */}
      <div className="conversation-messages-wrapper">
        <MessageList messages={messages} streamingMessageId={streamingMessageId} />

        {/* Agent 正在輸入指示 */}
        {streamingMessageId && agent?.status === 'typing' && <TypingIndicator />}
      </div>

      {/* 輸入框 */}
      <MessageInput
        onSend={sendMessage}
        disabled={isInputDisabled}
        isLoading={streamingMessageId !== null}
      />

      {/* 完成按鈕 (當對話完成時顯示) */}
      {/* 完成區塊：只有 missingFields 空且後端允許時才可觸發完成 API */}
      <div className="conversation-complete">
        <button
          className="complete-button"
          onClick={handleConversationEnd}
          disabled={!canComplete || isInputDisabled}
          title={!canComplete ? '請先補齊所有核心資訊再查看結果' : ''}
        >
          {canComplete ? '查看分析結果' : '資訊尚未齊全'}
        </button>
        {!canComplete && (
          <p className="complete-helper">
            尚有 {missingFields.length} 項資訊未完成，請繼續與 HouseIQ 對話。
          </p>
        )}
      </div>

      {/* 隱私承諾 */}
      <div className="conversation-footer">
        <p className="privacy-notice">
          🔒 <strong>隱私承諾:</strong> 您的對話已加密並安全存儲，我們絕不分享或用於其他目的。
        </p>
      </div>
    </div>
  );
}

export default ConversationUI;
