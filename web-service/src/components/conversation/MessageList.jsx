import React, { useEffect, useRef } from 'react';
import MessageItem from './MessageItem';

/**
 * Purpose: 渲染對話消息列表，並提供自動滾動到最新消息的功能。
 *
 * Input (Props):
 *   - messages (Array): 要顯示的消息物件陣列。
 *   - streamingMessageId (string | null): 正在串流中的 AI 消息 ID，用於傳遞給 MessageItem。
 *
 * Output:
 *   - 渲染一個消息列表。如果列表為空，則顯示一個空狀態提示。
 */
function MessageList({ messages, streamingMessageId }) {
  const messageEndRef = useRef(null);

  useEffect(() => {
    // 當新消息出現時，平滑地滾動到列表底部
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col space-y-4">
      {messages && messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
          <p className="text-4xl">💬</p>
          <p className="mt-4">開始對話來獲取個性化建議</p>
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