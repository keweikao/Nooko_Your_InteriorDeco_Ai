# Development Task List: AI 裝潢顧問 (AI Decor Advisor)

**Feature Branch**: `003-ai-decor-advisor`
**Created**: 2025-11-17
**Status**: Draft
**Input**: Refined plan, spec, visual style (Vakly), and component library (MagicUI).

## Phase 1: 核心基礎建設與最小可行對話迴圈 (Core Infrastructure & Minimum Viable Conversation Loop)

這個階段的目標是建立產品的骨幹，讓使用者能上傳檔案，並與 AI 進行一次最基本但有意義的對話。

### 後端 (Backend - analysis-service)

*   **Task 1.1: 檔案上傳與分派端點 (File Upload & Dispatch Endpoint)**
    *   **目標**: 建立一個高效、可靠的檔案接收機制，並將處理任務分派到背景。
    *   **子任務 1.1.1**: 在 `api/projects.py` 中，建立 `@router.post("/projects/{id}/upload")` 路由。
    *   **子任務 1.1.2**: 實作檔案類型驗證 (PDF, Excel, 圖片)。
    *   **子任務 1.1.3**: **快速預檢**：在儲存前，嘗試讀取檔案的標頭或元數據，若明顯損毀則立即回傳錯誤。
    *   **子任務 1.1.4**: 將上傳的原始檔案安全地儲存到 **Google Cloud Storage (GCS)**。
    *   **子任務 1.1.5**: 檔案儲存後，發送一個訊息到 **Cloud Pub/Sub** 或建立一個 **Cloud Task**，訊息中包含檔案的 GCS 路徑和 `project_id`。
    *   **子任務 1.1.6**: 立即回傳前端「上傳成功，排隊分析中」的訊息。

*   **Task 1.2: 檔案處理背景服務 (File Processing Background Service)**
    *   **目標**: 建立一個可擴展的背景服務，負責解析各種格式的報價單。
    *   **子任務 1.2.1**: 建立一個 **Cloud Function** 或背景 Worker，監聽 Task 1.1 建立的任務佇列。
    *   **子任務 1.2.2**: 從 GCS 下載檔案。
    *   **子任務 1.2.3**: **(技術選型)** 根據檔案類型，選擇解析器：
        *   如果是 Excel，使用 `openpyxl`。
        *   如果是文字型 PDF，使用 `pdfplumber`。
        *   如果是圖片或掃描型 PDF，呼叫 **Google Cloud Vision API** 進行 OCR。
    *   **子任務 1.2.4**: 將解析出的結構化文字或數據儲存到 Firestore 中，作為專案的 `original_quote_content`。
    *   **子任務 1.2.5**: 更新專案狀態為「分析完成」，並透過 Pub/Sub 或 Firestore 觸發前端的即時通知。

*   **Task 1.3: 對話串流端點 (SSE Conversation Endpoint)**
    *   **目標**: 建立一個能與前端進行即時、流暢對話的 API。
    *   **子任務 1.3.1**: 在 `api/projects.py` 中，建立 `@router.get("/projects/{id}/conversation/message-stream")` 路由。
    *   **子任務 1.3.2**: 實作 `event_generator`，接收前端 `message` 參數。
    *   **子任務 1.3.3**: 將收到的使用者訊息儲存到 Firestore 的 `messages` 子集合中。
    *   **子任務 1.3.4**: 呼叫 `gemini_service` 獲取 AI 回應，並將回應分塊 (chunk) 串流回前端。
    *   **子任務 1.3.5**: 儲存 AI 的完整回應到 Firestore。

*   **Task 1.4: Gemini 服務核心邏輯 (`gemini_service.py`)**
    *   **目標**: 實現 AI 的「單一核心，多重專家人格」對話邏輯。
    *   **子任務 1.4.1**: 確保 `generate_response_stream` 函式能接收並使用**完整的對話歷史**（已修復）。
    *   **子任務 1.4.2**: 實作 **Token 管理策略**：當對話歷史過長時，自動生成摘要並將其作為上下文的一部分傳遞給 Gemini API。
    *   **子任務 1.4.3**: 實作**使用者中心提問邏輯**：根據 `spec.md` 的要求，將技術問題轉譯為使用者能理解的、基於感受和成果的問題。
    *   **子任務 1.4.4**: 整合 `spec_tracking` 服務，動態調整系統提示 (system prompt)，引導 AI 收集缺失資訊。

### 前端 (Frontend - web-service)

*   **Task 1.5: 應用程式基礎佈局與風格導入**
    *   **目標**: 建立符合「Vakly」風格和「MagicUI」元件的基礎介面。
    *   **子任務 1.5.1**: 導入並配置 Tailwind CSS，定義全域樣式。
    *   **子任務 1.5.2**: 導入「Inter」字體，並設定字體大小、字重等排版規範。
    *   **子任務 1.5.3**: 建立基礎佈局，包含頁首、內容區與頁尾，並確保符合「Vakly」的簡潔、置中佈局風格。
    *   **子任務 1.5.4**: 導入 MagicUI 元件庫，並確保其與 Tailwind CSS 協同工作。

*   **Task 1.6: 檔案上傳元件 (`FileUpload.jsx`)**
    *   **目標**: 提供符合設計風格的檔案上傳介面。
    *   **子任務 1.6.1**: 建立元件 UI，包含拖拽區和上傳按鈕，遵循「Vakly」的卡片、按鈕風格和 MagicUI 元件。
    *   **子任務 1.6.2**: 實作 `handleFileChange` 和 `handleDrop` 事件。
    *   **子任務 1.6.3**: 建立 `handleUpload` 函式，呼叫後端的上傳端點 (`/api/projects/{id}/upload`)。
    *   **子任務 1.6.4**: 顯示上傳進度、成功或預檢失敗的狀態訊息。
    *   **子任務 1.6.5**: 上傳成功後，自動切換到對話介面。

*   **Task 1.7: 對話介面元件 (`ConversationUI.jsx`)**
    *   **目標**: 建立一個流暢、即時的對話互動介面。
    *   **子任務 1.7.1**: 建立 `MessageList.jsx` 子元件，用於渲染對話訊息列表，訊息氣泡採用「Vakly」的卡片風格。
    *   **子任務 1.7.2**: 建立 `MessageInput.jsx` 子元件，包含文字輸入框和發送按鈕，遵循 MagicUI 的互動模式。
    *   **子任務 1.7.3**: 在 `ConversationUI.jsx` 中管理 `messages` 狀態陣列。
    *   **子任務 1.7.4**: 實作一個掛鉤 (hook) 或服務，使用 `EventSource` API 連接後端的對話串流端點。
    *   **子任務 1.7.5**: 監聽 `onmessage` 事件，將收到的 AI 回應片段（chunk）更新到 `messages` 狀態中，實現打字機效果。
    *   **子任務 1.7.6**: 當使用者發送訊息時，觸發對後端 API 的呼叫。
    *   **子任務 1.7.7**: 設計一個不干擾的區域，顯示背景檔案處理的狀態（例如：「報價單分析中...」、「分析完成」）。

## Phase 2: 強化顧問體驗與核心價值交付 (Enhance Advisor Experience & Core Value Delivery)

這個階段的目標是實現產品的核心價值，讓 AI 顧問能提供專業的分析、建議和視覺化成果。

### 後端 (Backend - analysis-service)

*   **Task 2.1: 報價單分析與規格提取**
    *   **目標**: 將解析出的原始報價單內容，轉化為結構化的規格數據。
    *   **子任務 2.1.1**: 擴展 `gemini_service`，接收 `original_quote_content`。
    *   **子任務 2.1.2**: 實作 LLM 邏輯，從原始報價單內容中提取關鍵工項、材料、規格等資訊，並與 `spec_tracking` 服務對接。
    *   **子任務 2.1.3**: 實作 LLM 邏輯，判斷報價單的「及格」標準（完整性、合理性、潛在漏項），並生成分析結果。

*   **Task 2.2: 預算取捨建議邏輯**
    *   **目標**: 根據使用者提供的預算，生成客製化的建議。
    *   **子任務 2.2.1**: 擴展 `gemini_service`，接收使用者提供的預算範圍。
    *   **子任務 2.2.2**: 實作 LLM 邏輯，根據已提取的規格和預算，生成「不可妥協」和「可妥協」的工項建議。

*   **Task 2.3: 概念渲染圖生成服務**
    *   **目標**: 整合圖片生成模型，為使用者提供視覺化參考。
    *   **子任務 2.3.1**: 建立 `image_service.py`，封裝對圖片生成 API (例如 Google Imagen 或其他服務) 的呼叫。
    *   **子任務 2.3.2**: 擴展 `gemini_service`，在對話中根據使用者描述或風格偏好，呼叫 `image_service` 生成概念圖。
    *   **子任務 2.3.3**: 將生成的圖片 URL 儲存到 Firestore。

### 前端 (Frontend - web-service)

*   **Task 2.4: 對話中的圖片互動元件 (`ImageCarousel`/`ImageGrid`)**
    *   **目標**: 讓 AI 提供的圖片能與使用者互動。
    *   **子任務 2.4.1**: 建立元件 UI，遵循「Vakly」風格和 MagicUI 元件，能顯示多張圖片。
    *   **子任務 2.4.2**: 實作圖片點擊放大功能。
    *   **子任務 2.4.3**: 實作圖片選擇功能，將使用者偏好的圖片回傳給後端。

*   **Task 2.5: 最終成果展示頁面 (`SolutionPackage.jsx`)**
    *   **目標**: 優雅地呈現 AI 顧問的所有分析成果。
    *   **子任務 2.5.1**: 建立頁面 UI，遵循「Vakly」風格和 MagicUI 元件。
    *   **子任務 2.5.2**: 顯示標準化的「工程規格書」內容。
    *   **子任務 2.5.3**: 顯示生成的「概念渲染圖」。
    *   **子任務 2.5.4**: 顯示「預算取捨建議」。

## Phase 3: 商業閉環與優化 (Business Closure & Optimization)

這個階段的目標是將 AI 顧問的價值轉化為實際的商業機會，並確保系統的穩定性與安全性。

### 後端 (Backend - analysis-service)

*   **Task 3.1: 聯絡表單 API**
    *   **目標**: 接收使用者預約或諮詢的資訊。
    *   **子任務 3.1.1**: 在 `api/projects.py` 中，建立 `@router.post("/projects/{id}/contact")` 路由。
    *   **子任務 3.1.2**: 接收使用者姓名、電話等資訊，並儲存到 Firestore。
    *   **子任務 3.1.3**: (可選) 觸發內部通知（例如發送 Email 或 Slack 訊息給銷售團隊）。

*   **Task 3.2: 密鑰管理整合**
    *   **目標**: 確保所有敏感資訊的安全。
    *   **子任務 3.2.1**: 將所有 API 金鑰 (Gemini, Cloud Vision, Image Generation) 儲存到 **Google Secret Manager**。
    *   **子任務 3.2.2**: 修改服務啟動邏輯，從 Secret Manager 安全地讀取這些金鑰。

### 前端 (Frontend - web-service)

*   **Task 3.3: 最終行動呼籲 (CTA) 與聯絡表單**
    *   **目標**: 實現商業模式的最終轉換。
    *   **子任務 3.3.1**: 在 `SolutionPackage.jsx` 中，設計一個顯眼的「邀請我們施工」按鈕，遵循「Vakly」的主色按鈕風格。
    *   **子任務 3.3.2**: 點擊按鈕後，顯示一個簡單的聯絡表單（姓名、電話），遵循 MagicUI 元件風格。
    *   **子任務 3.3.3**: 表單提交後，呼叫後端 `contact` API。

## 測試與部署 (Testing & Deployment)

*   **Task 4.1: 單元測試與整合測試**
    *   **目標**: 確保程式碼品質和功能正確性。
    *   **子任務 4.1.1**: 為所有新的後端 API 端點和服務邏輯編寫 `pytest` 單元測試。
    *   **子任務 4.1.2**: 為前端關鍵元件編寫測試。
    *   **子任務 4.1.3**: 建立端到端 (E2E) 測試，驗證從檔案上傳到最終成果展示的完整流程。

*   **Task 4.2: 持續部署 (CI/CD) 優化**
    *   **目標**: 確保開發流程順暢，快速部署。
    *   **子任務 4.2.1**: 更新 `cloudbuild.yaml`，確保所有新的服務和依賴項都能正確建置和部署。
    *   **子任務 4.2.2**: 確保部署流程能安全地從 Secret Manager 讀取密鑰。
