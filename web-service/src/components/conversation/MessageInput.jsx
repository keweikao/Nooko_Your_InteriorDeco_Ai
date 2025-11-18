import React, { useState, useRef, useEffect } from 'react';
import { Send, LoaderCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';

/**
 * Purpose: 提供使用者輸入消息的介面，支持自動調整高度、Enter 發送和 Shift+Enter 換行。
 *
 * Input (Props):
 *   - onSend (function): 當使用者發送消息時觸發的回調函式，參數為消息內容 (string)。
 *   - disabled (boolean): 是否禁用輸入框和發送按鈕。
 *   - isLoading (boolean): 是否正在等待 AI 回應，用於顯示加載狀態。
 *
 * Output:
 *   - 渲染一個包含文字輸入區域和發送按鈕的表單。
 */
function MessageInput({ onSend, disabled = false, isLoading = false }) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  // 自動調整 textarea 高度以適應內容
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto'; // 重置高度
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`; // 設置新高度，最大 120px
    }
  }, [input]);

  const handleKeyDown = (e) => {
    // 處理 IME (輸入法編輯器) 狀態，避免在選字時觸發發送
    if (e.isComposing || e.nativeEvent.isComposing) return;
    
    // 當按下 Enter 且沒有按住 Shift 時，發送消息
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
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  return (
    <div className="relative">
      <Textarea
        ref={textareaRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="輸入您的消息... (Shift+Enter 換行)"
        disabled={disabled || isLoading}
        className="w-full pr-16 resize-none"
        rows="1"
      />
      <Button
        type="submit"
        size="icon"
        onClick={handleSend}
        disabled={!input.trim() || disabled || isLoading}
        className="absolute top-1/2 right-3 -translate-y-1/2"
        title={disabled ? '等待 Agent 回應' : '發送消息 (Enter)'}
      >
        {isLoading ? (
          <LoaderCircle className="h-5 w-5 animate-spin" />
        ) : (
          <Send className="h-5 w-5" />
        )}
        <span className="sr-only">發送消息</span>
      </Button>
    </div>
  );
}

export default MessageInput;