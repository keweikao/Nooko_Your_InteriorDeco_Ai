# 裝潢 AI 夥伴 (Nooko - Your Interior Deco AI)

歡迎使用「裝潢 AI 夥伴」！這是一個創新的專案，旨在利用多 Agent AI 系統，協助使用者分析室內設計的報價單，探索需求，並最終產出專業的規格建議和風格渲染圖。

## 專案架構

本專案採用前後端分離的微服務架構：

-   **`analysis-service` (後端)**:
    -   使用 Python, FastAPI 開發。
    -   核心是由三個 AI Agent 組成的系統：
        1.  **客戶經理 (Client Manager Agent)**: 與使用者互動，收集需求。
        2.  **專業統包商 (Contractor Agent)**: 根據需求產生詳細的工程規格與報價。
        3.  **設計師 (Designer Agent)**: 根據需求產生概念渲染圖。
    -   所有對外的服務（LLM、資料庫、圖片生成）目前皆使用**模擬 (Mock) 服務**，以便在本地進行開發和測試。

-   **`web-service` (前端)**:
    -   使用 React (Vite) 開發。
    -   提供使用者介面，包括檔案上傳、聊天互動、最終成果展示和預約表單。

## 環境準備

在開始之前，請確保您的開發環境已安裝以下工具：

-   [Python](https://www.python.org/) (建議版本 3.9+)
-   [Node.js](https://nodejs.org/) (建議版本 18+)
-   `pip` (Python 套件管理工具)
-   `npm` (Node.js 套件管理工具)

## 本地啟動指南

請依照以下步驟啟動後端和前端服務。

### 1. 啟動後端 (`analysis-service`)

首先，設定並啟動後端 FastAPI 服務。

```bash
# 1. 進入後端服務目錄
cd analysis-service

# 2. 建立虛擬環境
python -m venv venv

# 3. 啟用虛擬環境
#    - macOS / Linux:
source venv/bin/activate
#    - Windows:
#      .\venv\Scripts\activate

# 4. 安裝依賴套件
pip install -r requirements.txt

# 5. 啟動 FastAPI 服務
#    服務將會運行在 http://127.0.0.1:8000
uvicorn src.main:app --reload
```

### 2. 啟動前端 (`web-service`)

接著，在**新的終端機視窗**中，設定並啟動前端 React 應用程式。

```bash
# 1. 進入前端服務目錄
cd web-service

# 2. 安裝依賴套件
npm install

# 3. 啟動 Vite 開發伺服器
#    服務將會運行在 http://127.0.0.1:5173 (或其他可用埠號)
npm run dev
```

#### UI Showcase（僅限 Staging）

前端有一個實驗性的 MagicUI / shadcn 元件展示頁。預設不會顯示，只有在 staging/測試環境需要展示元件時，才在建置或部署前設定：

```bash
export VITE_ENABLE_UI_SHOWCASE=true
```

Cloud Run 部署時可透過 build arg / ENV 將此變數設為 `true`，正式環境請保持預設值（或不設定）以僅顯示互動流程。

### 3. 瀏覽應用程式

當兩個服務都成功啟動後，您可以開啟瀏覽器，進入前端服務的網址（通常是 `http://127.0.0.1:5173`）來查看應用程式的 UI。

> **注意**: 目前前端 UI 會逐步展示各個開發完成的頁面。最新的頁面是預約表單。若要查看其他頁面（如聊天介面、最終成果頁），您需要手動修改 `web-service/src/App.jsx` 檔案。

## 目前進度與後續步驟

我們已經完成了所有核心使用者故事的原型開發，包括所有 Agent 的基本邏輯和前端 UI 頁面。

接下來的重點將會是：
-   撰寫單元測試。
-   將服務容器化 (Docker)。
-   設定 CI/CD 流程，準備部署到雲端。
-   將模擬服務替換為真實的 GCP 服務（Vertex AI, Firestore, GCS 等）。

## 雲端部署與 Firestore 設定

1. **Cloud Build / Cloud Run**
    - `cloudbuild.yaml` 會同時建置並部署 `analysis-service` 與 `web-service`。請在觸發建置時設定以下 substitutions：
        - `_TAG_NAME`: 建議使用 `main` 最新 commit 的短 SHA。
        - `_REGION`: 預設為 `asia-east1`，可依需求覆寫。
        - `_API_BASE_URL`: 提供前端於建置階段注入的 API 根網址（例如完成部署後的 `analysis-service` 公開網址 `/api`）。
    - 後端部署時會自動帶上 `DB_BACKEND=firestore`，確保 Cloud Run 執行環境使用 Firestore 資料層。
    - 建議建立 Cloud Build 觸發器綁定主要分支，確保 `/deploy` 之後會自動推送至 Cloud Run。

2. **Firestore 與服務帳號**
    - `analysis-service` 會根據 `DB_BACKEND` 選擇資料層；Cloud Run 上請使用具備 `roles/datastore.user` 的服務帳號，並確保 `GOOGLE_CLOUD_PROJECT` 能夠連線到 Firestore（Native 模式）。
    - 預設集合名稱為 `projects`。可透過環境變數 `FIRESTORE_PROJECTS_COLLECTION` 或 `FIRESTORE_PROJECT_ID` 覆寫。
    - 任何 Booking API (`/api/projects/book`) 的請求都會寫入 Firestore，方便後續追蹤。

3. **前端環境變數**
    - `web-service/Dockerfile` 會在建置階段使用 `VITE_APP_API_BASE_URL` 來打包靜態檔案，來源即為 Cloud Build 的 `_API_BASE_URL` substitution。
    - 若需要在本地測試，請於 `web-service/.env.local` 設定 `VITE_APP_API_BASE_URL=http://127.0.0.1:8000/api` 後再執行 `npm run dev`。

更多部署細節與 MCP 指令，可參考 `docs/deployment.md`。
