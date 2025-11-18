import { useState, useCallback, useEffect } from 'react';

const stageDescriptions = {
  greeting: '開始對話',
  scope: '了解裝修範圍',
  lifestyle: '了解生活與空間使用',
  budget: '釐清預算與時程',
  construction: '確認施工細節',
  summary: '資訊已齊備，可準備分析'
};

/**
 * Purpose: 管理整個對話流程的 React Hook，包括消息狀態、與後端 SSE 的通訊、進度追蹤等。
 *
 * Input:
 *   - projectId (string): 當前專案的唯一識別碼。
 *   - apiBaseUrl (string): 後端 API 的基礎 URL。
 *
 * Output (Object):
 *   - messages (Array): 對話消息列表。
 *   - agent (Object): 當前對話的 AI Agent 資訊。
 *   - progress (Object): 對話進度狀態 { current, stage, description }。
 *   - missingFields (Array): AI 認為還需要補充的資訊欄位列表。
 *   - canComplete (boolean): 是否可以結束對話並查看結果。
 *   - loading (boolean): 是否正在進行初始化。
 *   - error (string | null): 錯誤訊息。
 *   - isConnected (boolean): SSE 是否已成功連接。
 *   - streamingMessageId (string | null): 正在串流中的 AI 消息 ID。
 *   - sendMessage (function): 發送使用者消息的函式。
 *   - completeConversation (function): 結束對話並請求最終分析結果的函式。
 *   - setProgress (function): 手動設置進度的函式 (主要用於調試)。
 */
function useConversation(projectId, apiBaseUrl) {
  const [messages, setMessages] = useState([]);
  const [agent, setAgent] = useState(null);
  const [progress, setProgress] = useState({
    current: 0,
    stage: 'greeting',
    description: '開始對話...'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [streamingMessageId, setStreamingMessageId] = useState(null);
  const [missingFields, setMissingFields] = useState([]);

  /**
   * Purpose: 初始化對話，通過調用後端 /conversation/init 端點獲取初始訊息和 Agent 資訊。
   * Input: 無。
   * Output: 更新 messages, agent, progress, isConnected, missingFields 等狀態。
   */
  const initConversation = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `${apiBaseUrl}/projects/${projectId}/conversation/init`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            timestamp: new Date().toISOString()
          })
        }
      );

      if (!response.ok) {
        throw new Error(`初始化失敗: ${response.statusText}`);
      }

      const data = await response.json();

      setAgent(data.agent);

      if (data.initialMessage) {
        const initialMessage = {
          id: `msg-${Date.now()}`,
          conversationId: data.conversationId,
          sender: 'agent',
          content: data.initialMessage,
          timestamp: data.timestamp || Date.now(),
          status: 'sent'
        };
        setMessages([initialMessage]);
      }

      setIsConnected(true);
      setProgress({
        current: 0,
        stage: 'greeting',
        description: stageDescriptions.greeting
      });
      setMissingFields([]);
    } catch (err) {
      console.error('初始化對話失敗:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [projectId, apiBaseUrl]);

  /**
   * Purpose: 發送使用者消息並通過 SSE 接收 AI 的流式回應。
   * Input: content (string): 使用者輸入的消息內容。
   * Output: 更新 messages, agent, progress, missingFields, streamingMessageId 等狀態。
   */
  const sendMessage = useCallback(
    async (content) => {
      try {
        setError(null);
        const userMessage = {
          id: `msg-${Date.now()}`,
          conversationId: 'current',
          sender: 'user',
          content: content.trim(),
          timestamp: Date.now(),
          status: 'sending'
        };

        setMessages((prev) => [...prev, userMessage]);

        setTimeout(() => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === userMessage.id ? { ...msg, status: 'sent' } : msg
            )
          );
        }, 100);

        setAgent((prev) => ({ ...prev, status: 'typing' }));

        const eventSource = new EventSource(
          `${apiBaseUrl}/projects/${projectId}/conversation/message-stream?message=${encodeURIComponent(content)}`
        );

        let agentResponseId = `msg-${Date.now()}-agent`;
        let agentResponseContent = '';

        eventSource.addEventListener('message_chunk', (event) => {
          const data = JSON.parse(event.data);
          console.log('Received message_chunk:', data);

          if (!agentResponseContent) {
            const agentMessage = {
              id: agentResponseId,
              conversationId: 'current',
              sender: 'agent',
              content: data.chunk || '',
              timestamp: Date.now(),
              status: 'sent',
              metadata: data.metadata
            };
            setMessages((prev) => [...prev, agentMessage]);
            setStreamingMessageId(agentResponseId);
            console.log('Set streamingMessageId:', agentResponseId);
          }

          agentResponseContent += data.chunk || '';

          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === agentResponseId
                ? { ...msg, content: agentResponseContent }
                : msg
            )
          );

          if (data.metadata) {
            if (data.metadata.stage) {
              setProgress((prev) => ({
                ...prev,
                stage: data.metadata.stage,
                description: stageDescriptions[data.metadata.stage] || prev.description
              }));
            }
            if (data.metadata.progress !== undefined) {
              setProgress((prev) => ({
                ...prev,
                current: data.metadata.progress
              }));
            }
            if (data.metadata.missingFields) {
              setMissingFields(data.metadata.missingFields);
            }
          }

          if (data.isComplete) {
            console.log('Received isComplete: true. Closing EventSource.');
            setAgent((prev) => ({ ...prev, status: 'idle' }));
            setStreamingMessageId(null);
            console.log('Cleared streamingMessageId.');
            eventSource.close();
          }
        });

        eventSource.addEventListener('error', (error) => {
          console.error('SSE 連接錯誤:', error);
          setAgent((prev) => ({ ...prev, status: 'idle' }));
          setStreamingMessageId(null);
          console.log('Cleared streamingMessageId due to error.');
          eventSource.close();
        });
      } catch (err) {
        console.error('發送消息失敗:', err);
        setError(err.message);
      }
    },
    [projectId, apiBaseUrl]
  );

  /**
   * Purpose: 請求結束對話並獲取最終分析結果。
   * Input: 無。
   * Output: 成功時返回分析結果 (Object)，失敗時返回 null 並更新 error 狀態。
   */
  const completeConversation = useCallback(async () => {
    try {
      if (missingFields.length > 0) {
        setError('還有資訊尚未補齊，請先回答完所有提問。');
        return null;
      }

      const response = await fetch(
        `${apiBaseUrl}/projects/${projectId}/conversation/complete`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        }
      );

      if (!response.ok) {
        const detail = await response.json().catch(() => null);
        const message = detail?.detail?.message || detail?.detail || response.statusText;
        throw new Error(message);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      console.error('完成對話失敗:', err);
      setError(err.message);
      return null;
    }
  }, [projectId, apiBaseUrl, missingFields.length]);

  useEffect(() => {
    initConversation();
  }, [initConversation]);

  return {
    messages,
    agent,
    progress,
    missingFields,
    canComplete: missingFields.length === 0 && progress.stage === 'summary',
    loading,
    error,
    isConnected,
    streamingMessageId,
    sendMessage,
    completeConversation,
    setProgress
  };
}

export default useConversation;