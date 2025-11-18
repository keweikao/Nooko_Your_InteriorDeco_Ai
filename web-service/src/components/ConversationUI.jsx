import React from 'react';
import AgentCard from './conversation/AgentCard';
import MessageList from './conversation/MessageList';
import MessageInput from './conversation/MessageInput';
import TypingIndicator from './conversation/TypingIndicator';
import ConversationProgress from './conversation/ConversationProgress';
import useConversation from '../hooks/useConversation';


import { Button as UiButton } from './ui/button';

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
      <div className="flex flex-col items-center justify-center h-full text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        <p className="mt-4 text-muted-foreground">初始化對話中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center text-destructive">
        <p className="text-4xl">⚠️</p>
        <p className="mt-4">{error}</p>
        <UiButton onClick={() => window.location.reload()} className="mt-4">重試</UiButton>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto bg-card border border-border rounded-lg shadow-lg p-4 sm:p-6 space-y-4">
      {/* Header */}
      <div className="text-center border-b border-border pb-4">
        <h1 className="text-2xl font-bold text-primary">HouseIQ 裝潢 AI 夥伴</h1>
        <p className="text-sm text-muted-foreground">與 HouseIQ 進行需求訪談</p>
      </div>

      {/* Agent Card */}
      <AgentCard agent={agent} />

      {/* Progress Indicator */}
      <ConversationProgress progress={progress} />

      {/* Message Area */}
      <div className="flex-grow overflow-y-auto p-4 bg-background rounded-md border border-border min-h-[400px]">
        <MessageList messages={messages} streamingMessageId={streamingMessageId} />
        {streamingMessageId && agent?.status === 'typing' && <TypingIndicator />}
      </div>

      {/* Input Box */}
      <MessageInput
        onSend={sendMessage}
        disabled={isInputDisabled}
        isLoading={streamingMessageId !== null}
      />

      {/* Completion Button */}
      <div className="pt-4 border-t border-border text-center">
        <UiButton
          onClick={handleConversationEnd}
          disabled={!canComplete || isInputDisabled}
          className="w-full sm:w-auto"
        >
          {canComplete ? '查看分析結果' : '資訊尚未齊全'}
        </UiButton>
      </div>

      {/* Privacy Notice */}
      <div className="text-center">
        <p className="text-xs text-muted-foreground">
          🔒 <strong>隱私承諾:</strong> 您的對話已加密並安全存儲，我們絕不分享或用於其他目的。
        </p>
      </div>
    </div>
  );
}

export default ConversationUI;
