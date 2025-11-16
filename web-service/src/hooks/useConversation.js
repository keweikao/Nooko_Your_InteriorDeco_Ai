import { useState, useCallback, useEffect } from 'react';

/**
 * 對話邏輯 Hook
 * 管理：消息、Agent 狀態、進度、SSE 連接
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

  /**
   * 初始化對話 - 調用後端 /conversation/init 端點
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

      // 設置 Agent 信息
      setAgent(data.agent);

      // 添加初始問候消息
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
        current: 10,
        stage: 'greeting',
        description: '開始對話'
      });
    } catch (err) {
      console.error('初始化對話失敗:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [projectId, apiBaseUrl]);

  /**
   * 發送消息並接收 SSE 流式回應
   */
  const sendMessage = useCallback(
    async (content) => {
      try {
        // 添加用戶消息
        const userMessage = {
          id: `msg-${Date.now()}`,
          conversationId: 'current',
          sender: 'user',
          content: content.trim(),
          timestamp: Date.now(),
          status: 'sending'
        };

        setMessages((prev) => [...prev, userMessage]);

        // 更新用戶消息狀態為已發送
        setTimeout(() => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === userMessage.id ? { ...msg, status: 'sent' } : msg
            )
          );
        }, 100);

        // 設置 Agent 為輸入狀態
        setAgent((prev) => ({ ...prev, status: 'typing' }));

        // 建立 SSE 連接
        const eventSource = new EventSource(
          `${apiBaseUrl}/projects/${projectId}/conversation/message-stream?message=${encodeURIComponent(content)}`
        );

        let agentResponseId = `msg-${Date.now()}-agent`;
        let agentResponseContent = '';

        eventSource.addEventListener('message_chunk', (event) => {
          const data = JSON.parse(event.data);

          if (!agentResponseContent) {
            // 首次 chunk，添加新消息
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
          }

          agentResponseContent += data.chunk || '';

          // 更新流式消息內容
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === agentResponseId
                ? { ...msg, content: agentResponseContent }
                : msg
            )
          );

          // 更新進度信息
          if (data.metadata) {
            if (data.metadata.stage) {
              setProgress((prev) => ({
                ...prev,
                stage: data.metadata.stage
              }));
            }
            if (data.metadata.progress !== undefined) {
              setProgress((prev) => ({
                ...prev,
                current: data.metadata.progress
              }));
            }
          }

          // 檢查是否完成
          if (data.isComplete) {
            setAgent((prev) => ({ ...prev, status: 'idle' }));
            setStreamingMessageId(null);
            eventSource.close();
          }
        });

        eventSource.addEventListener('error', (error) => {
          console.error('SSE 連接錯誤:', error);
          setAgent((prev) => ({ ...prev, status: 'idle' }));
          setStreamingMessageId(null);
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
   * 完成對話
   */
  const completeConversation = useCallback(async () => {
    try {
      const response = await fetch(
        `${apiBaseUrl}/projects/${projectId}/conversation/complete`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        }
      );

      if (!response.ok) {
        throw new Error(`完成對話失敗: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      console.error('完成對話失敗:', err);
      setError(err.message);
      return null;
    }
  }, [projectId, apiBaseUrl]);

  /**
   * 組件掛載時初始化對話
   */
  useEffect(() => {
    initConversation();
  }, [initConversation]);

  return {
    messages,
    agent,
    progress,
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
