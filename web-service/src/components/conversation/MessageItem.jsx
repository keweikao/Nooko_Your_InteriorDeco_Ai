import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ThumbsUp, ZoomIn } from 'lucide-react';
import { Button } from '../ui/button';

/**
 * Purpose: 渲染單一的對話消息，能根據 message.type 顯示文字或圖片。
 *          支持點擊放大圖片、流式打字機效果，並區分使用者和 AI Agent 的樣式。
 *
 * Input (Props):
 *   - message (Object): 消息物件，包含 sender, content, type, timestamp, status 等。
 *   - isStreaming (boolean): 指示此消息是否正在從後端流式傳輸中。
 *
 * Output:
 *   - 渲染一個帶有頭像、消息氣泡（文字或圖片）和時間戳的對話消息項。
 */
function MessageItem({ message, isStreaming = false }) {
  const [displayText, setDisplayText] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const isAgent = message.sender === 'agent';
  const isImage = message.type === 'image';

  useEffect(() => {
    if (isStreaming && !isImage) {
      let currentIndex = 0;
      const interval = setInterval(() => {
        if (currentIndex < message.content.length) {
          setDisplayText(message.content.substring(0, currentIndex + 1));
          currentIndex++;
        } else {
          clearInterval(interval);
        }
      }, 20);
      return () => clearInterval(interval);
    } else {
      setDisplayText(message.content);
    }
  }, [message.content, isStreaming, isImage]);

  const handleImageClick = () => {
    if (isImage) {
      setIsModalOpen(true);
    }
  };

  const handleSelectImage = (e) => {
    e.stopPropagation(); // Prevent modal from opening
    console.log(`Image selected: ${message.content}`);
    // Placeholder for Task 2.4.3 - sending preference to backend
  };

  const bubbleVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
  };

  const renderContent = () => {
    if (isImage) {
      return (
        <div className="relative group">
          <img
            src={message.content}
            alt="AI generated concept"
            className="rounded-lg max-w-xs cursor-pointer"
            onClick={handleImageClick}
          />
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity rounded-lg">
            <ZoomIn className="text-white h-12 w-12" />
          </div>
        </div>
      );
    }
    return (
      <>
        <p className="whitespace-pre-wrap">{displayText}</p>
        {isStreaming && <span className="inline-block w-2 h-4 bg-current animate-pulse ml-1"></span>}
      </>
    );
  };

  return (
    <>
      <motion.div
        className={`flex items-start gap-3 ${isAgent ? 'justify-start' : 'justify-end'}`}
        variants={bubbleVariants}
        initial="hidden"
        animate="visible"
      >
        {isAgent && (
          <div className="relative flex-shrink-0">
            <img src="https://placehold.co/40x40/EBF0F4/7C8490?text=A&font=sans" alt="Agent Avatar" className="w-10 h-10 rounded-full" />
            <span className="absolute bottom-0 right-0 block w-3 h-3 bg-green-500 border-2 border-white rounded-full"></span>
          </div>
        )}

        <div className={`flex flex-col ${isAgent ? 'items-start' : 'items-end'}`}>
          <div
            className={`max-w-md lg:max-w-lg rounded-2xl ${
              isAgent
                ? `bg-muted text-muted-foreground rounded-bl-none ${isImage ? 'p-2' : 'px-4 py-3'}`
                : `bg-primary text-primary-foreground rounded-br-none px-4 py-3`
            }`}
          >
            {renderContent()}
          </div>
          {isImage && isAgent && (
            <Button variant="ghost" size="sm" className="mt-2" onClick={handleSelectImage}>
              <ThumbsUp className="h-4 w-4 mr-2" />
              喜歡這個風格
            </Button>
          )}
          <span className="text-xs text-muted-foreground mt-1 px-1">
            {new Date(message.timestamp).toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        {!isAgent && message.status !== 'sent' && (
          <div className="flex-shrink-0 self-end pb-6">
            {message.status === 'sending' && <span title="傳送中">⏱️</span>}
            {message.status === 'error' && <span title="傳送失敗">❌</span>}
          </div>
        )}
      </motion.div>

      {isModalOpen && (
        <div
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50"
          onClick={() => setIsModalOpen(false)}
        >
          <img
            src={message.content}
            alt="Enlarged view"
            className="max-w-[90vw] max-h-[90vh] object-contain"
          />
        </div>
      )}
    </>
  );
}

export default MessageItem;
