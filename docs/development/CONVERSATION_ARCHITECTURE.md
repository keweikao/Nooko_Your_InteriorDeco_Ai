# Agent1 真實對話系統 - 架構設計

## 📋 系統概述

將現有的問卷問答系統轉換為真實的 AI 對話體驗，用戶可以與 Agent1 (施工主任) 進行自由的多輪對話。

## 🏗️ 架構組件

### 1. 前端組件結構

```
src/components/
├── ConversationUI.jsx          # 主對話容器組件
├── ConversationUI.css          # 對話樣式
├── conversation/
│   ├── MessageList.jsx         # 消息列表容器
│   ├── MessageItem.jsx         # 單條消息組件
│   ├── AgentCard.jsx           # Agent 卡片 (頭像、名稱、狀態)
│   ├── MessageInput.jsx        # 消息輸入框
│   ├── TypingIndicator.jsx     # Agent 正在輸入的動畫
│   └── ConversationProgress.jsx # 進度指示
├── hooks/
│   └── useConversation.js      # 對話邏輯 Hook
├── utils/
│   └── conversationManager.js  # 消息管理工具
└── types/
    └── conversation.ts         # TypeScript 類型定義
```

### 2. 數據結構

```typescript
// Message 類型
interface Message {
  id: string;                    // 唯一標識符
  conversationId: string;        // 所屬對話
  sender: 'user' | 'agent';      // 發送者
  content: string;               // 消息內容
  timestamp: number;             // 時間戳
  status: 'sending' | 'sent' | 'error';  // 消息狀態
  metadata?: {
    category?: string;           // 對於 Agent：問題類別
    confidence?: number;         // 信心度
  }
}

// Conversation 類型
interface Conversation {
  id: string;
  projectId: string;
  messages: Message[];
  agent: {
    name: string;               // "施工主任"
    avatar: string;             // 頭像 URL
    status: 'idle' | 'typing' | 'analyzing';
  }
  progress: {
    current: number;            // 0-100
    stage: 'greeting' | 'assessment' | 'clarification' | 'summary' | 'complete';
  }
  metadata: {
    startedAt: number;
    updatedAt: number;
    estimatedCompletionTime?: number;
  }
}
```

### 3. API 端點設計

#### 3.1 初始化對話
```
POST /projects/{projectId}/conversation/init
Response:
{
  conversationId: string,
  agent: { name, avatar },
  initialMessage: string,
  timestamp: number
}
```

#### 3.2 流式發送消息 (SSE)
```
POST /projects/{projectId}/conversation/{conversationId}/message-stream
Body: { content: string }
Response: Server-Sent Events 流
Event: "message_chunk"
Data: { chunk: string, isComplete: boolean }
```

#### 3.3 查詢對話歷史
```
GET /projects/{projectId}/conversation/{conversationId}/history
Response:
{
  messages: Message[],
  progress: { current, stage },
  summary?: string
}
```

#### 3.4 完成對話
```
POST /projects/{projectId}/conversation/{conversationId}/complete
Response:
{
  summary: string,
  briefing: ProjectBrief,
  analysis: {...}
}
```

## 🎨 UI 流程

### 消息流程圖
```
用戶輸入消息
    ↓
禁用輸入框 + 顯示發送狀態
    ↓
發送消息到後端
    ↓
顯示用戶消息 (sent 狀態)
    ↓
顯示 TypingIndicator (Agent 思考中)
    ↓
SSE 流式接收 Agent 回應
    ↓
逐字流式顯示 Agent 消息
    ↓
消息完成，恢復輸入框
    ↓
檢測對話是否完成
```

### 頁面佈局
```
┌─────────────────────────────────────────┐
│        HouseIQ 裝潢 AI 夥伴 - 訪談          │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ [Agent 頭像] 施工主任 (在線)      │   │
│  │ 進度: ████░░░░░░░░░ 40% | 評估中  │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ 消息區域                        │   │
│  │                                 │   │
│  │ Agent: 根據您的預算...          │   │
│  │                                 │   │
│  │ User: 30 萬以內                 │   │
│  │                                 │   │
│  │ Agent: [typing animation...]    │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ [文本框] 輸入您的回答...          │   │
│  │           [發送按鈕] [停止]      │   │
│  └─────────────────────────────────┘   │
│                                         │
│  隱私承諾: 您的對話已加密...            │
└─────────────────────────────────────────┘
```

## 🔄 數據流

### 初始化流程
```
ConversationUI 掛載
  ↓
useEffect: 調用 initConversation()
  ↓
POST /conversation/init
  ↓
獲得 conversationId 和初始消息
  ↓
渲染初始 Agent 問候消息
```

### 消息提交流程
```
用戶輸入 → handleSendMessage()
  ↓
創建 Message { sender: 'user', content, status: 'sending' }
  ↓
添加到 messageList (樂觀更新)
  ↓
POST /message-stream { content }
  ↓
設置 agent.status = 'typing'
  ↓
SSE EventSource 開始接收
  ↓
Event 'message_chunk':
  - 流式追加 Agent 消息
  - 逐字動畫顯示
  ↓
Event 'message_complete':
  - 設置 agent.status = 'idle'
  - 更新進度信息
  ↓
重新啟用輸入框
```

## 🎯 核心功能

### 1. 消息流式顯示
- 使用 SSE (Server-Sent Events) 實時推送
- 前端逐字動畫渲染
- 流暢的文本流效果

### 2. 對話歷史
- 完整的消息記錄
- 支持滾動查看之前的對話
- 消息時間戳

### 3. Agent 狀態
- idle: 等待用戶輸入
- typing: 正在輸入回應
- analyzing: 分析用戶答案

### 4. 進度追蹤
- 5 個階段: greeting → assessment → clarification → summary → complete
- 每個階段的進度百分比
- 自動檢測完成條件

## 🛠️ 實現清單

- [ ] 創建 types/conversation.ts 類型定義
- [ ] 創建 hooks/useConversation.js (狀態邏輯)
- [ ] 創建 utils/conversationManager.js (SSE 管理)
- [ ] 創建 ConversationUI.jsx (主容器)
- [ ] 創建 conversation/MessageList.jsx
- [ ] 創建 conversation/MessageItem.jsx
- [ ] 創建 conversation/AgentCard.jsx
- [ ] 創建 conversation/MessageInput.jsx
- [ ] 創建 conversation/TypingIndicator.jsx
- [ ] 創建 ConversationUI.css (樣式)
- [ ] 更新後端 API 端點
- [ ] 集成 App.jsx
- [ ] 測試和調整

## 📱 響應式設計
- 桌面: 完整 3 列佈局 (側邊欄 + 消息 + 信息面板)
- 平板: 2 列 (消息 + 側邊欄)
- 手機: 單列 (消息 + 底部輸入)

## 🔒 數據安全
- 所有消息通過 HTTPS 傳輸
- SSE 連接安全認證
- 消息不存儲於 localStorage (隱私)
- 會話自動過期

## ⚡ 性能優化
- 虛擬滾動處理大量消息
- 消息去重 (避免重複渲染)
- SSE 自動重連機制
- 內存管理: 保留最近 100 條消息
