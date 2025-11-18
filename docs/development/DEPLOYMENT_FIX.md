# 部署修復說明

## 問題描述

用戶報告在訪問 https://web-service-33840733430.asia-east1.run.app/ 時，「開始使用」按鈕無法點擊。

## 根本原因分析

### 1. 環境變數配置錯誤
前端應用程式被配置為連接到錯誤的後端 API URL：

- **配置的 URL**: `https://analysis-service-33840733430.asia-east1.run.app/api`
- **實際的 URL**: `https://analysis-service-cdixz5p6gq-de.a.run.app/api`

### 2. 按鈕禁用機制
在 `web-service/src/App.jsx:91`，「開始使用」按鈕使用了條件禁用：

```javascript
<button
  className="primary-button"
  onClick={() => setCurrentStep('upload')}
  disabled={!projectId}  // 當 projectId 為 null 時按鈕被禁用
>
  開始使用 →
</button>
```

當 API 無法連接時：
1. `createNewProject` 函數失敗
2. `projectId` 保持為 `null`
3. 按鈕因此被禁用無法點擊

### 3. 部署流程問題
原本的 `cloudbuild.yaml` 使用了硬編碼的佔位符 URL (`_API_BASE_URL` substitution)，需要手動提供正確的 URL。如果提供錯誤的 URL，前端會連接失敗。

## 解決方案

### 更新 Cloud Build 配置
修改 `cloudbuild.yaml`，使其能夠動態獲取並使用正確的 API URL：

1. **部署 analysis-service**
   - 先部署後端服務到 Cloud Run

2. **動態獲取 URL**
   ```yaml
   - name: 'gcr.io/cloud-builders/gcloud'
     entrypoint: 'bash'
     args:
       - '-c'
       - |
         gcloud run services describe analysis-service \
           --region=${_REGION} \
           --format='value(status.url)' > /workspace/analysis_service_url.txt
         echo "Analysis Service URL: $(cat /workspace/analysis_service_url.txt)"
     id: Get Analysis Service URL
   ```

3. **使用正確的 URL 建置 web-service**
   ```yaml
   - name: 'gcr.io/cloud-builders/docker'
     entrypoint: 'bash'
     args:
       - '-c'
       - |
         ANALYSIS_URL=$(cat /workspace/analysis_service_url.txt)
         echo "Building web-service with API URL: $${ANALYSIS_URL}/api"
         docker build \
           -t gcr.io/${PROJECT_ID}/web-service:${_TAG_NAME} \
           --build-arg VITE_APP_API_BASE_URL=$${ANALYSIS_URL}/api \
           /workspace/web-service
     id: Build Web Service Image
   ```

4. **部署 web-service**
   - 前端現在會連接到正確的後端 API

### 關鍵改進

- **移除硬編碼的 URL**：不再需要 `_API_BASE_URL` substitution
- **自動化配置**：前後端 URL 自動匹配，無需手動配置
- **錯誤預防**：消除了人為配置錯誤的可能性

## 部署命令

```bash
# 獲取當前 commit hash
git rev-parse --short HEAD

# 部署應用程式
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_TAG_NAME=deploy-<commit-hash>,_REGION=asia-east1
```

## 測試驗證

使用提供的測試腳本驗證部署：

```bash
./test_deployment.sh
```

該腳本會：
1. 獲取服務 URL
2. 測試 API endpoint (創建專案)
3. 測試 web service 可訪問性
4. 報告測試結果

## 預期結果

修復後：
- ✅ 前端能成功連接到後端 API
- ✅ `projectId` 正確獲取
- ✅ 「開始使用」按鈕可以點擊
- ✅ 用戶可以正常使用應用程式

## 技術細節

### Cloud Build 工作目錄
- Cloud Build 將程式碼複製到 `/workspace` 目錄
- Docker build context 必須使用絕對路徑：`/workspace/web-service`
- 不同的 build step 共享 `/workspace` 目錄和文件

### Vite 環境變數
- 在建置階段通過 `--build-arg` 傳遞 `VITE_APP_API_BASE_URL`
- Vite 會在編譯時將環境變數嵌入到靜態檔案中
- 部署後的應用程式使用編譯時的 API URL

## 未來改進建議

1. **健康檢查**: 在前端添加 API 連線健康檢查，提供更友好的錯誤訊息
2. **重試機制**: 實現自動重試邏輯，處理暫時性的網路問題
3. **環境變數驗證**: 在建置階段驗證 API URL 的可達性
4. **監控告警**: 設置 Cloud Monitoring 告警，及時發現部署問題

## 參考資料

- Cloud Build 文檔: https://cloud.google.com/build/docs
- Cloud Run 文檔: https://cloud.google.com/run/docs
- Vite 環境變數: https://vitejs.dev/guide/env-and-mode.html
