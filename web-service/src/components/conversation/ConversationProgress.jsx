import React from 'react';

/**
 * Purpose: 顯示當前對話進度的 UI 元件，包括進度條和階段描述。
 *
 * Input (Props):
 *   - progress (Object): 進度物件，包含 current (百分比), stage (階段名稱), description (階段描述)。
 *
 * Output:
 *   - 渲染一個包含進度百分比、進度條和當前階段描述的 UI 元件。
 */
function ConversationProgress({ progress }) {
  const currentProgress = progress?.current || 0;
  const currentDescription = progress?.description || '正在初始化...';

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center text-sm font-medium">
        <span className="text-muted-foreground">{currentDescription}</span>
        <span className="font-bold text-primary">{currentProgress}%</span>
      </div>
      <div className="w-full bg-muted rounded-full h-2.5">
        <div
          className="bg-primary h-2.5 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${currentProgress}%` }}
        ></div>
      </div>
    </div>
  );
}

export default ConversationProgress;