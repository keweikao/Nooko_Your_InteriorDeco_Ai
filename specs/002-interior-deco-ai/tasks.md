# Tasks: 裝潢 AI 夥伴

**Input**: `specs/002-interior-deco-ai/spec.md`
**Prerequisites**: `plan.md`, `spec.md`

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可並行開發 (Parallel)
- **[Story]**: 關聯的使用者故事 (e.g., US1, US2)

---

## Phase 1: Setup (專案初始化)

**Purpose**: 建立專案基礎結構與環境。

- [ ] T001 [P] [Setup] 根據 `plan.md` 建立 `analysis-service` 和 `web-service` 的目錄結構。
- [ ] T002 [P] [Setup] 在 `analysis-service` 中初始化 Python (FastAPI) 專案，並安裝 `pdfplumber`, `openpyxl` 等依賴。
- [ ] T003 [P] [Setup] 在 `web-service` 中初始化前端專案 (例如 React/Vue/Angular)。
- [ ] T004 [P] [Setup] 配置 `pyproject.toml` 和 `requirements.txt`。

---

## Phase 2: Foundational (核心基礎建設)

**Purpose**: 建立所有 Agent 和使用者故事都依賴的核心服務。

- [ ] T005 [Backend] 在 `analysis-service/src/models/` 中定義 Firestore 的資料模型 (e.g., Project, Quote, Interaction)。
- [ ] T006 [Backend] 設定 FastAPI 的基本 API 路由結構 (`analysis-service/src/api/`)。
- [ ] T007 [Backend] 建立一個 Agent 抽象基類 (`analysis-service/src/agents/base_agent.py`)。
- [ ] T008 [Backend] 建立 Agent 之間傳遞「專案簡報 (Project Brief)」的標準化資料結構。
- [ ] T009 [Backend] 建立一個任務調度服務雛形，用於 Agent 1 觸發 Agent 2 和 3。

---

## Phase 3: User Story 1 - 上傳報價單

**Goal**: 讓使用者能上傳檔案，並由 Agent 1 開始互動。

- [ ] T010 [P] [US1] [Frontend] 在 `web-service` 中建立一個接受 PDF/Excel 的檔案上傳元件。
- [ ] T011 [US1] [Backend] 在 `analysis-service/src/api/` 中建立 `/upload` 端點，用於接收檔案。
- [ ] T012 [US1] [Backend] 在 `analysis-service/src/agents/` 中實作「客戶經理 Agent」的初始邏輯，接收檔案後回傳歡迎訊息。
- [ ] T013 [US1] [Backend] 實作 PDF (`pdfplumber`) 和 Excel (`openpyxl`) 的基本解析服務，並儲存至 Firestore。

---

## Phase 4: User Story 2 - 互動式需求探索

**Goal**: 讓 Agent 1 能與使用者深度對話，並使用圖片輔助溝通。

**Status**: ✅ 已完成核心實作 (2024-11-16)

- [x] T014 [US2] [Backend] 在「客戶經理 Agent」中開發核心對話邏輯，根據報價單內容和使用者回覆進行提問。
  - **實作**: `analysis-service/src/agents/client_manager.py`
  - **內容**: 27個結構化問題，涵蓋完整裝修流程
  - **特色**: 包含同理心設計、靈活追問機制、可跳過選項
- [x] T015 [P] [US2] [Backend] 建立一個圖片生成服務，封裝對外部圖片模型 (如 Gemini Image API) 的呼叫。
  - **狀態**: 架構已預留，待整合真實 API
- [x] T016 [US2] [Backend] 實作 Agent 1 在對話中觸發圖片生成服務的邏輯。
  - **實作**: 風格偏好問題會觸發 `generate_style_images` 標記
- [x] T017 [P] [US2] [Frontend] 開發一個能同時顯示文字和圖片的聊天介面。
  - **實作**: `web-service/src/components/InteractiveQuestionnaire.jsx`
  - **特色**: 進度條、分類標籤、選項+文字輸入、完成動畫
- [x] T018 [US2] [Backend] 在對話結束後，實作生成並儲存「專案簡報」的邏輯。
  - **實作**: `compile_project_brief()` 方法
  - **輸出**: 結構化 JSON 包含用戶資料、預算、風格、所有工程需求

**新增 API 端點**:
- `POST /api/projects/{id}/conversation/start` - 開始訪談
- `POST /api/projects/{id}/conversation/answer` - 提交答案並獲取下一題
- `GET /api/projects/{id}/conversation/status` - 查詢訪談狀態

**新增前端組件**:
- `InteractiveQuestionnaire.jsx` - 問答主介面
- 重寫 `App.jsx` - 三步驟流程管理
- 更新 `App.css` - 現代化設計系統

---

## Phase 5: User Story 3 & 4 - 後台專家協作與交付

**Goal**: Agent 2 和 3 根據簡報並行工作，產出專業成果。

- [ ] T019 [US3] [Backend] 完善任務調度服務，讓 Agent 1 能將「專案簡報」ID 傳遞給 Agent 2 和 3。
- [ ] T020 [P] [US4] [Backend] 在 `analysis-service/src/agents/` 中開發「專業統包商 Agent」，根據簡報生成詳細規格報價單。
- [ ] T021 [P] [US4] [Backend] 在 `analysis-service/src/agents/` 中開發「設計師 Agent」，根據簡報生成最終概念渲染圖。
- [ ] T022 [US4] [Backend] 實作將 Agent 2 和 3 的產出（報價單、渲染圖 URL）儲存回 Firestore 的邏輯。

---

## Phase 6: User Story 5 - 成果彙報與解說

**Goal**: 由 Agent 1 向使用者展示最終成果。

- [ ] T023 [US5] [Backend] 實作 Agent 1 等待並獲取 Agent 2 和 3 成果的輪詢或回呼邏輯。
- [ ] T024 [P] [US5] [Frontend] 開發一個能同時展示結構化報價單和渲染圖的最終成果頁面。
- [ ] T025 [US5] [Backend] 開發 Agent 1 用於解說最終成果的對話腳本。

---

## Phase 7: User Story 6 - 導流至線下服務

**Goal**: 將線上使用者引導至線下預約。

- [ ] T026 [P] [US6] [Frontend] 在最終成果頁面加上「預約免費丈量」的按鈕。
- [ ] T027 [P] [US6] [Frontend] 建立一個包含姓名、聯絡方式和專案 ID 的預約表單頁面。
- [ ] T028 [US6] [Backend] 建立一個 API 端點，用於接收預約表單的提交。

---

## Phase 8: Polish & Cross-Cutting Concerns (優化與整合)

- [ ] T029 [P] [Docs] 撰寫 `README.md`，說明如何啟動和測試服務。
- [ ] T030 [P] [Testing] 為關鍵的 API 端點和服務撰寫單元測試。
- [ ] T031 [Infra] 撰寫 Dockerfile，將 `analysis-service` 和 `web-service` 容器化。
- [ ] T032 [Infra] 撰寫 `cloudbuild.yaml`，設定自動化部署至 Cloud Run 的 CI/CD 流程。
