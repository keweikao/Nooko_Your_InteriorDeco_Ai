# 後端 SSE 端點實現文檔

## 概述

已成功實現 Plan B (真實對話系統) 所需的三個 SSE 端點。這些端點使前端 ConversationUI 組件能夠與 Agent1 進行實時流式對話。

---

## 實現的三個端點

### 1. `POST /projects/{project_id}/conversation/init`

**功能**: 初始化真實對話

**請求**:
```http
POST /projects/{project_id}/conversation/init
Content-Type: application/json
```

**響應** (200 OK):
```json
{
  "conversationId": "conv-550e8400-e29b-41d4-a716-446655440000",
  "agent": {
    "name": "施工主任",
    "avatar": "🤖",
    "status": "idle"
  },
  "initialMessage": "歡迎！我是您的專業施工主任...",
  "timestamp": 1700000000000
}
```

**說明**:
- 為新對話創建會話 ID
- 初始化對話上下文和消息歷史
- 返回 Agent 信息和初始問候消息
- 消息已優化為中文，提高用戶體驗

---

### 2. `POST /projects/{project_id}/conversation/message-stream`

**功能**: 發送消息並接收 SSE 流式回應

**請求**:
```http
POST /projects/{project_id}/conversation/message-stream?message=用戶消息
Content-Type: text/event-stream
```

**響應** (SSE Stream):
```
event: message_chunk
data: {"chunk":"感","isComplete":false,"metadata":{"stage":"assessment","progress":25}}

event: message_chunk
data: {"chunk":"謝","isComplete":false,"metadata":{"stage":"assessment","progress":25}}

event: message_chunk
data: {"chunk":"您","isComplete":false,"metadata":{"stage":"assessment","progress":25}}

...

event: message_chunk
data: {"chunk":"","isComplete":true,"metadata":{"stage":"assessment","progress":25}}
```

**說明**:
- 支持自然語言對話
- 實現逐字符流式傳輸（支持中文）
- 自動根據用戶消息選擇對應的回應
- 包含進度和階段元數據
- 響應頭正確配置防止緩衝和連接問題

**前端連接示例**:
```javascript
const eventSource = new EventSource(
  `${apiBaseUrl}/projects/${projectId}/conversation/message-stream?message=${encodeURIComponent(content)}`
);

eventSource.addEventListener('message_chunk', (event) => {
  const data = JSON.parse(event.data);
  // 處理流式數據
  if (data.isComplete) {
    eventSource.close();
  }
});
```

---

### 3. `POST /projects/{project_id}/conversation/complete`

**功能**: 完成對話並返回分析結果

**請求**:
```http
POST /projects/{project_id}/conversation/complete
Content-Type: application/json
```

**響應** (200 OK):
```json
{
  "summary": "基於我們的對話，我已經了解了您的需求。以下是我的專業建議：...",
  "briefing": {
    "project_id": "proj-123",
    "user_profile": {
      "communication_style": "professional",
      "budget_conscious": true,
      "timeline_important": true
    },
    "style_preferences": ["modern", "practical"],
    "key_requirements": [
      "防水處理",
      "安全電氣",
      "通風系統",
      "材料質量"
    ],
    "completed_at": "2025-11-16T14:30:00.000Z"
  },
  "analysis": {
    "summary": "...",
    "key_insights": [
      "用戶對質量有高要求",
      "預算有限制，需要合理分配",
      "多個區域需要關注防水"
    ],
    "recommendations": [
      "優先安排隱蔽工程檢查",
      "選擇高品質防水材料",
      "建議分階段施工以控制成本"
    ],
    "next_steps": [
      "生成詳細設計圖",
      "準備完整規格書",
      "安排現場丈量"
    ]
  }
}
```

**說明**:
- 完成對話流程
- 返回對話總結
- 包含項目簡報數據
- 提供專業分析和建議
- 支持後續的結果頁面展示

---

## 技術實現細節

### SSE 配置

所有端點使用正確的 SSE 響應頭：

```python
headers={
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",  # 禁用 Nginx 緩衝
    "Connection": "keep-alive"
}
media_type="text/event-stream"
```

### 數據存儲

- **conversations_db**: 存儲對話會話 (內存式，可替換為 Firestore)
- **projects_db**: 與現有專案存儲集成

### Agent 回應生成

目前實現了簡單的基於關鍵字的回應系統：

```python
async def generate_agent_response(message: str, conversation_id: str):
    # 根據消息內容選擇對應回應
    # 逐字符流式發送
    # 支持長回應自動分塊
```

**未來改進**: 可以替換為調用 `llm_service.call_llm_streaming()` 以支持真正的 AI 生成回應。

---

## 前端集成

### 1. ConversationUI 會自動調用這些端點

前端通過 `useConversation` hook 自動集成：

```javascript
// 初始化
await fetch(`${apiBaseUrl}/projects/${projectId}/conversation/init`, {
  method: 'POST'
})

// 發送消息
const eventSource = new EventSource(
  `${apiBaseUrl}/projects/${projectId}/conversation/message-stream?message=...`
)

// 完成對話
await fetch(`${apiBaseUrl}/projects/${projectId}/conversation/complete`, {
  method: 'POST'
})
```

### 2. 完整工作流程

```
用戶進入訪談 → init 端點 → 獲得 Agent 信息 + 初始消息
                ↓
          用戶輸入消息
                ↓
        message-stream 端點 → SSE 流式回應
                ↓
          Agent 回應顯示
                ↓
          用戶繼續對話
                ↓
       完成對話 → complete 端點 → 返回分析結果
```

---

## 測試 API

### 使用 cURL 測試

```bash
# 1. 初始化對話
curl -X POST http://localhost:8000/projects/test-123/conversation/init

# 2. 發送消息（SSE 流式）
curl -X POST "http://localhost:8000/projects/test-123/conversation/message-stream?message=廚房裝修"

# 3. 完成對話
curl -X POST http://localhost:8000/projects/test-123/conversation/complete
```

### 使用 Python 測試

```python
import requests
import json

API_BASE = "http://localhost:8000"
project_id = "test-123"

# 1. 初始化
response = requests.post(f"{API_BASE}/projects/{project_id}/conversation/init")
print(json.dumps(response.json(), ensure_ascii=False, indent=2))

# 2. 發送消息（SSE）
response = requests.post(
    f"{API_BASE}/projects/{project_id}/conversation/message-stream?message=廚房裝修",
    stream=True
)
for line in response.iter_lines():
    if line:
        print(line.decode())

# 3. 完成對話
response = requests.post(f"{API_BASE}/projects/{project_id}/conversation/complete")
print(json.dumps(response.json(), ensure_ascii=False, indent=2))
```

---

## 部署說明

### 生產環境注意事項

1. **LLM 服務集成**
   - 目前使用簡單的關鍵字回應
   - 建議替換為真正的 LLM 流式調用（如 OpenAI API）

2. **持久化存儲**
   - 當前使用內存存儲
   - 生產環境應使用 Firestore 或 PostgreSQL

3. **會話管理**
   - 實現會話超時和清理機制
   - 添加消息加密和隱私保護

4. **監控和日誌**
   - 添加詳細的日誌記錄
   - 實現性能監控和錯誤追蹤

5. **錯誤處理**
   - 添加更詳細的錯誤消息
   - 實現自動重試機制

---

## 檔案位置

- **API 端點實現**: `analysis-service/src/api/projects.py`
- **前端集成**: `web-service/src/components/ConversationUI.jsx`
- **狀態管理**: `web-service/src/hooks/useConversation.js`
- **類型定義**: `web-service/src/types/conversation.ts`

---

## 後續改進

### 短期 (1-2 週)
- [ ] 集成真正的 LLM 流式服務
- [ ] 添加消息數據庫持久化
- [ ] 實現會話恢復機制

### 中期 (2-4 週)
- [ ] 多語言支持
- [ ] 對話分析和洞察提取
- [ ] 用戶反饋機制

### 長期 (1+ 月)
- [ ] 多 Agent 支持
- [ ] 專家評審流程
- [ ] 高級分析和建議引擎

---

**部署日期**: 2025-11-16
**實現狀態**: ✅ 完成
**測試狀態**: ⚠️ 需進一步測試
**生產就緒**: ❌ 需完成上述改進
