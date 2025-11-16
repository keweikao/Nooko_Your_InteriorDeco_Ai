import React, { useEffect, useRef } from 'react';
import MessageItem from './MessageItem';
import '../ConversationUI.css';

/**
 * 消息列表容器
 * 支持自動滾動到最新消息
 */
function MessageList({ messages, streamingMessageId }) {
  const messageEndRef = useRef(null);

  useEffect(() => {
    // 自動滾動到最新消息
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="message-list">
      {messages && messages.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-icon">💬</p>
          <p className="empty-state-text">開始對話來獲取個性化建議</p>
        </div>
      ) : (
        <>
          {messages.map((message) => (
            <MessageItem
              key={message.id}
              message={message}
              isStreaming={streamingMessageId === message.id}
            />
          ))}
          <div ref={messageEndRef} />
        </>
      )}
    </div>
  );
}

export default MessageList;
