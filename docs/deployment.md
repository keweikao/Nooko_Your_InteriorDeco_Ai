# 雲端部署與 MCP 操作手冊

本手冊說明如何透過 MCP 工具將 `analysis-service` 與 `web-service` 部署到 Cloud Run，並驗證 Firestore 資料。請在 Claude Code / Claude Desktop 啟用 `@modelcontextprotocol/server-gcloud` 與 `custom_firestore` 之後再依序執行。

## 1. 建置與部署

1. **設定 Substitutions**
    - `_TAG_NAME`: 建議設定為該次部署 commit 的短 SHA。
    - `_REGION`: 預設 `asia-east1`。
    - `_API_BASE_URL`: 後端公開網址（含 `/api`），供前端建置使用。
2. **觸發 Cloud Build**
```python
mcp__gcloud.build_submit({
    "source": ".",
    "config": "cloudbuild.yaml",
    "substitutions": {
        "_TAG_NAME": "main-<SHORT_SHA>",
        "_REGION": "asia-east1",
        "_API_BASE_URL": "https://analysis-service-xxxx.a.run.app/api"
    }
})
```
3. **部署完成後確認服務**
```python
mcp__gcloud.run_services_describe({
    "service": "analysis-service",
    "region": "asia-east1"
})
mcp__gcloud.run_services_describe({
    "service": "web-service",
    "region": "asia-east1"
})
```
4. **檢查日誌**
```python
mcp__gcloud.logging_read({
    "service": "analysis-service",
    "severity": "ERROR",
    "limit": 5
})
```

## 2. Firestore 設定與驗證

1. **預設集合**：`projects`。可透過 `FIRESTORE_PROJECTS_COLLECTION` 覆寫。
2. **服務帳號**：Cloud Run 執行帳號需具備 `roles/datastore.user`。
3. **示範查詢**
```python
mcp__firestore.firestore_query({
    "collection": "projects",
    "filters": [
        {"field": "status", "op": "==", "value": "booked"}
    ],
    "context_mode": "minimal",
    "limit": 5
})
```
4. **以 API 觸發寫入**：對 `https://analysis-service-xxxx.a.run.app/api/projects/book` 發送 POST 請求，之後再用上方指令驗證新增的 booking。

## 3. Cloud Build 觸發器建議

1. 建議建立兩個觸發器：
    - `analysis-service-deploy`: 監聽主分支，觸發 `cloudbuild.yaml`。
    - `web-service-deploy`: 可共用同一份 `cloudbuild.yaml`，依需要覆寫 `_API_BASE_URL`。
2. 使用以下 `gcloud` 指令（在 MCP `run_cmd` 中執行）：
```python
mcp__gcloud.run_cmd({
    "command": [
        "gcloud", "beta", "builds", "triggers", "create", "github",
        "--name=interior-ai-deploy",
        "--repo-name=HouseIQ_Your_InteriorDeco_Ai",
        "--repo-owner=<OWNER>",
        "--branch-pattern=^main$",
        "--build-config=cloudbuild.yaml"
    ]
})
```

完成上述設定後，即可透過 `/deploy` → Cloud Build → Cloud Run 的流程，將最新程式碼自動釋出至雲端，並使用 MCP 工具檢視部署結果與 Firestore 狀態。***
