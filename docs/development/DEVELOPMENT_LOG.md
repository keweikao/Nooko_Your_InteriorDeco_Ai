## 2025年11月18日 - 專案名稱變更為「HouseIQ」及新功能規劃

### 總結
應使用者要求，啟動了將專案名稱從「Nooko」變更為「HouseIQ」的全面性工作。此變更涉及程式碼、配置、文件中的多處引用。同時，使用者提出了移除「產出專屬藍圖」步驟以及在檔案上傳後進行 OCR 並將結果儲存至 Firestore 的新功能需求。

### 已完成任務詳情 (專案名稱變更 - Phase 1)
- **更新 `pyproject.toml`**: 將專案名稱和描述中的 "Nooko" 替換為 "HouseIQ"。
- **更新 `README.md`**: 將專案標題中的 "Nooko" 替換為 "HouseIQ"。
- **更新 `analysis-service/src/api/projects.py`**: 更新 GCS 儲存桶名稱、GCP 專案 ID 預設值和歡迎訊息，將 "Nooko" 替換為 "HouseIQ"。
- **更新 `analysis-service/src/services/image_service.py`**: 更新 GCS 圖片儲存桶名稱和專案 ID 預設值，將 "Nooko" 替換為 "HouseIQ"。
- **更新 `analysis-service/src/services/gemini_service.py`**: 更新專案 ID 預設值，將 "Nooko" 替換為 "HouseIQ"。
- **更新 `analysis-service/src/services/secret_service.py`**: 更新專案 ID 預設值，將 "Nooko" 替換為 "HouseIQ"。
- **更新 `analysis-service/src/agents/client_manager.py`**: 更新歡迎訊息，將 "Nooko" 替換為 "HouseIQ"。
- **更新 `analysis-service/src/services/pdf_service.py`**: 更新 PDF 標題，將 "Nooko" 替換為 "HouseIQ"。
- **更新 `web-service/src/App.jsx`**: 更新歡迎訊息、文字、標題和版權資訊，將 "Nooko" 替換為 "HouseIQ"。
- **更新 `web-service/src/components/ConversationUI.jsx`**: 更新標題，將 "Nooko" 替換為 "HouseIQ"。
- **更新 `web-service/src/index.css`**: 更新註解，將 "Nooko" 替換為 "HouseIQ"。
- **更新 `web-service/src/App.css`**: 將所有對 "Nooko" 的引用替換為 "HouseIQ"，包括註解和變數名稱。
- **更新 `web-service/tailwind.config.js`**: 更新品牌顏色註解和品牌名稱，將 "Nooko" 替換為 "HouseIQ"。
- **更新 `QUICK_START.sh`**: 更新註解、啟動訊息和 tmux session 名稱，將 "Nooko" 替換為 "HouseIQ"。
- **更新 `test_deployment.sh`**: 更新註解和測試訊息，將 "Nooko" 替換為 "HouseIQ"。
- **更新 `docs/deployment.md`**: 更新 repo 名稱，將 "Nooko_Your_InteriorDeco_Ai" 替換為 "HouseIQ_Your_InteriorDeco_Ai"。
- **更新 `docs/credential-management.md`**: 更新服務帳戶名稱，將 "nooko-ai-service-account" 替換為 "houseiq-ai-service-account"。
- **更新 `cloudbuild.yaml`**: 更新服務帳戶參考，將 "nooko-ai-develop" 替換為 "houseiq-ai-develop"。
- **更新 `docs/development/CONVERSATION_ARCHITECTURE.md`**: 更新標題，將 "Nooko" 替換為 "HouseIQ"。

### 待處理任務 (專案名稱變更 - Phase 1 續)
- **更新 `docs/development/START_TESTING.md`**: 更新標題、歡迎頁面描述，「Nooko 裝潢 AI 夥伴」替換為「HouseIQ 裝潢 AI 夥伴」。
- **更新 `docs/development/USER_FLOW.md`**: 更新標題、歡迎訊息。
- **更新 `docs/development/IMPLEMENTATION_SUMMARY.md`**: 更新標題。
- **更新 `docs/development/UPDATES_SUMMARY.md`**: 更新標題。
- **更新 `docs/development/LOCAL_TESTING_GUIDE.md`**: 更新標題、歡迎頁面描述，「Nooko 裝潢 AI 夥伴」替換為「HouseIQ 裝潢 AI 夥伴」。
- **更新 `docs/development/DEVELOPMENT_LOG.md`**: 更新品牌顏色註解。
- **更新 `docs/development/PLAN_B_IMPLEMENTATION_SUMMARY.md`**: 更新維護者。
- **更新 `docs/development/FIXED_START_GUIDE.md`**: 更新 tmux session 名稱、標題。
- **更新 `tools/project_search/README.md`**: 更新專案根目錄。

### 新功能需求規劃
- **移除「產出專屬藍圖」步驟**:
    *   識別前端 (`web-service`) 中定義工作流程步驟的位置。
    *   修改前端程式碼以移除此步驟。
- **檔案上傳後進行 OCR 並儲存至 Firestore**:
    *   修改 `background-processor/main.py` 以添加 OCR 功能並將結果儲存在 Firestore 中。
    *   更新 `background-processor/requirements.txt` 以包含新的依賴項。
    *   更新 Cloud Vision API 和 Firestore 的 IAM 權限。

### 後續步驟
1.  繼續完成專案名稱變更的剩餘文件更新。
2.  處理移除「產出專屬藍圖」步驟的需求。
3.  規劃並實作檔案上傳後 OCR 至 Firestore 的功能。
4.  在所有變更完成後，重新部署並驗證所有服務。[2025-11-18 17:49:52] - 開始執行 Cloud Run 部署程序，遵循 QUICK_START_FOR_AI.md v3.0 指示。
[2025-11-18 18:05:00] - 更新 `cloudbuild.yaml` 使 Cloud Build、Cloud Run 與 Cloud Functions 全數使用現有的 `nooko-ai-develop` 服務帳戶，解決 404 無法建立建置的問題。
[2025-11-18 18:08:00] - 修正 `cloudbuild.yaml` 中部署步驟的環境變數設定，改用 `--set-env-vars` 傳入 PROJECT_ID/DB_BACKEND/PYTHONDONTWRITEBYTECODE，避免 gcloud run deploy 出現未識別參數錯誤。
[2025-11-18 18:10:00] - 將 Cloud Build 內 gcloud 部署參數改為直接使用服務帳戶 email，並同步更新說明，避免 Cloud Run/Functions 因 resource path 格式不支援而部署失敗。
[2025-11-18 18:20:00] - 調查檔案上傳錯誤（Cloud Run 日誌顯示無法存取 `houseiq-project-quotes`），確認原因為 GCS bucket 尚未建立；已建立 `gs://houseiq-project-quotes`（region: asia-east1）供上傳使用。
[2025-11-18 18:35:00] - 更新 `analysis-service/src/services/gemini_service.py`，改為優先使用 Secret Manager 中的 `GEMINI_API_KEY` 建立 Gemini Client，並在無法使用 API key 時自動回退至 Vertex AI，確保無需額外權限即可完成對話。
[2025-11-18 18:35:00] - 更新 `tools/test_vertex.py`，讓測試腳本支援 `GEMINI_BACKEND` 與 `GEMINI_API_KEY`，可與服務端一致地切換 API Key / Vertex 兩種呼叫模式。
[2025-11-18 18:45:00] - 將 `cloudbuild.yaml` 的 Cloud Run 部署環境變數加入 `GEMINI_BACKEND=api`，確保 analysis-service 在部署後會直接使用 Secret Manager 中的 API Key 連線 Gemini。
[2025-11-18 18:45:09] - Refactored gemini_service.py to use Vertex AI directly, simplifying initialization and improving error handling.
[2025-11-18 19:18:00] - 補上 `analysis-service/src/api/projects.py` 的 `import re`，解決 Cloud Run SSE 流程中 `name 're' is not defined` 導致回覆失敗的問題。
[2025-11-18 19:35:00] - 將預設模型切換為 `gemini-2.5-flash-lite` 並在 `cloudbuild.yaml` 注入 `GEMINI_MODEL_NAME`，同時更新 `tools/test_vertex.py` 以反映最新模型。
[2025-11-18 19:50:00] - 將 `analysis-service/src/services/gemini_service.py` 改回純 API Key 初始化（`genai.Client(api_key=...)`），完全移除 Vertex 依賴以避免再次出現 `genai.configure` 錯誤。
[2025-11-18 20:57:22] - Feat: Integrated a new state-aware dynamic prompt system into GeminiLLMService based on the detailed user-provided prompt. The system now follows a five-stage conversational flow to guide users through quote analysis.
