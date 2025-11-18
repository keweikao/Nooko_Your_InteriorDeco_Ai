import React from 'react';

const statusConfig = {
  idle: { text: '待命中', color: 'bg-green-500' },
  typing: { text: '正在輸入...', color: 'bg-yellow-500' },
  analyzing: { text: '分析中...', color: 'bg-blue-500' },
  default: { text: '離線', color: 'bg-gray-400' },
};

/**
 * Purpose: 顯示 AI Agent 資訊的卡片，包括頭像、名稱、狀態和簡介。
 *
 * Input (Props):
 *   - agent (Object): Agent 物件，包含 name, avatar, status 等資訊。
 *
 * Output:
 *   - 渲染一個包含 Agent 詳細資訊的卡片式 UI 元件。
 */
function AgentCard({ agent }) {
  const currentStatus = statusConfig[agent?.status] || statusConfig.default;

  return (
    <div className="flex items-center gap-4 p-4 bg-muted/50 rounded-lg border border-border">
      <div className="relative flex-shrink-0">
        <img
          src={agent?.avatar || 'https://placehold.co/40x40/EBF0F4/7C8490?text=A&font=sans'}
          alt={agent?.name || 'Agent'}
          className="w-12 h-12 rounded-full"
        />
        <span
          className={`absolute bottom-0 right-0 block w-3.5 h-3.5 ${currentStatus.color} border-2 border-muted rounded-full`}
          title={currentStatus.text}
        ></span>
      </div>

      <div className="flex-grow">
        <h2 className="font-bold text-primary">{agent?.name || 'HouseIQ'}</h2>
        <p className="text-sm text-muted-foreground">{currentStatus.text}</p>
      </div>
    </div>
  );
}

export default AgentCard;