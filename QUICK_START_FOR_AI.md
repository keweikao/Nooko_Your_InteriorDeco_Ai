# AI 助理快速上手指南 (v3.0)

**目的**: 讓任何 AI 助理都能快速理解「AI 裝潢顧問」專案的最新方向，並遵循最佳實踐進行開發。
**閱讀時間**: 3 分鐘

---

## 🚀 專案速覽 (Project at a Glance)

- **產品定位 (Positioning)**:
  一個專業、中立的**「AI 裝潢顧問」**，為已有報價單但充滿疑慮的屋主提供第二意見，解決他們看不懂、怕被坑、擔心漏項的痛點。

- **核心流程 (Core Flow)**:
  1.  **分析**: 使用者上傳現有報價單。
  2.  **互動**: AI 透過引導式對話補全個人化需求。
  3.  **交付**: 產出包含「工程規格書」、「預算取捨建議」和「概念渲染圖」的解決方案包。

- **商業目標 (Business Goal)**:
  透過提供價值和建立信任，最終引導使用者選擇**我們的施工服務**，並承諾以 AI 產出的規格書作為合作基礎。

---

## 🏛️ 核心架構原則 (Core Architectural Principles)

1.  **單一 AI 核心，多重專家人格 (Single AI Core, Multiple Expert Personas)**:
    - 後端由一個統一、強大的 `gemini_service` 驅動，避免舊版多 Agent 的複雜性。
    - 透過 Prompt Engineering 指示單一模型模擬不同專家（顧問、統包、設計師）的思維模式，確保對話體驗流暢無中斷。

2.  **非同步處理管線 (Asynchronous Processing Pipeline)**:
    - **上傳與分派**: API 端點 (`/upload`) 只負責快速接收檔案、存入 Google Cloud Storage (GCS) 並觸發背景任務 (via Pub/Sub 或 Cloud Tasks)。
    - **背景處理**: 由獨立的 Cloud Function 執行耗時的解析工作（OCR、Excel/PDF 讀取），完成後將結果存入 Firestore。

3.  **即時狀態更新 (Real-time State Updates)**:
    - 前端透過 **Server-Sent Events (SSE)** 與後端建立長連線。
    - 後端在背景任務的各個階段（如「分析中」、「分析完成」）主動推送狀態給前端，提供流暢的即時體驗。

4.  **Token 管理策略 (Token Management Strategy)**:
    - 為避免超出模型上下文視窗限制，需實作「滾動式摘要」機制。當對話歷史過長時，自動將舊對話摘要成精簡文本，再與近期對話結合後送入模型。

---

## 🎨 UI/UX 風格指南 (UI/UX Style Guide)

- **整體美學 (Aesthetic)**:
  遵循 "Vakly" 範本的**現代、簡潔、專業**風格。強調大量的留白、置中的內容和整齊的版面。

- **顏色與字體 (Color & Typography)**:
  - **顏色**: 以中性色（白、灰、黑）為基礎，搭配一個鮮明的品牌主色（如赤陶色 #E2725B）來凸顯按鈕和重點。
  - **字體**: 全站使用 **Inter** 作為主要字體，透過不同粗細來建立資訊層次感。

- **元件庫 (Component Library)**:
  - 所有前端互動元件，應優先使用或參考 **MagicUI** 的風格和互動模式來建構。
  - **元件風格**: 圓角、細緻的邊框或柔和的陰影，以提升精緻感。

---

## 核心開發原則 (Core Development Principles)

1.  **⚠️ 效率優先 (Efficiency First)**
    - **目標**: 為了節省您的 Token 消耗和成本。
    - **實踐**: 在讀取檔案 (`read_file`) 前，優先使用更經濟的工具（如 `grep`, `search_file_content`, `ls`）來縮小範圍、確認檔案是否存在或定位關鍵程式碼。避免不必要的全檔案讀取。

2.  **✍️ 程式碼註解 (Code Commenting)**
    - **目標**: 提升程式碼的可讀性與可維護性。
    - **實踐**: 對於所有主要的函式或類別，必須在定義上方加入註解塊。註解應包含：
        - **目的 (Purpose)**：簡述該函式/類別的核心職責。
        - **輸入 (Input)**：說明重要的參數及其來源。
        - **輸出 (Output)**：說明回傳值的內容和目的地。

3.  **✍️ 即時記錄日誌 (Log as You Go)**
    - 每完成一個**主要動作** (例如：成功修改一個檔案、從一次探索中獲得結論)，就**必須**立即在 `DEVELOPMENT_LOG.md` 中記錄進度。
    - **禁止**等到整個任務結束後才一次性補寫日誌。

4.  **🗣️ 統一語言 (Unified Language)**
    - 所有對使用者的回覆、註解和日誌記錄，一律使用**繁體中文**。

5.  **🚀 標準化提交與部署 (Standardized Commit & Deployment)**
    - **流程**: `git add` ➜ `git commit` ➜ `git push` ➜ `gcloud builds submit`。
    - **提交訊息**: 遵循 Conventional Commits 規範 (例如 `feat:`, `fix:`, `docs:`)，清晰描述變更。
    - **部署指令**: `gcloud builds submit . --config cloudbuild.yaml --project=nooko-yourinteriordeco-ai`。

---

## 📚 專案上下文快速查閱 (Quick Context Lookup)

- **上次進度？** → `DEVELOPMENT_LOG.md`
- **專案架構？** → `specs/002-interior-deco-ai/plan.md`
- **功能規格？** → `specs/002-interior-deco-ai/spec.md`
- **開發任務？** → `specs/002-interior-deco-ai/tasks.md`

---

## ✅ 任務開始前自我檢查 (Final Self-Check)

- [ ] 我已理解新的「AI 裝潢顧問」專案願景與核心架構。
- [ ] 我會遵循「效率優先」原則，謹慎使用 `read_file`。
- [ ] 我承諾會**即時更新** `DEVELOPMENT_LOG.md`。
- [ ] 我將遵循 `add` -> `commit` -> `push` -> `gcloud` 的標準化部署流程。

---
*文件版本: 3.0*
*上次更新: 2025-11-17*
*主要變更: 全面更新以反映新的產品方向、架構原則、UI 風格及 AI 助理協作流程。*