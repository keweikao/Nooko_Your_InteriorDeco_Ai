# Nooko – Interior Deco AI Workspace

Nooko 是一個以 GitHub Spec Kit 為基礎的室內設計自動化工作空間。此版本保留完整的 Spec-Driven Development (SDD) 骨架、SOP、MCP 工具與自動化設定，讓我們能專注在打造室內設計 AI 能力。

## 🚀 內容概覽
- **Automation**：`Makefile`、`pyproject.toml`、根目錄 `Dockerfile*` 與核心腳本，確保本地與 CI/CD 指令一致。
- **Spec Kit 核心**：`.specify/`、`templates/`、`QUICK_START_FOR_AI.md`、`DEVELOPMENT_GUIDELINES.md`、`TOKEN_OPTIMIZATION_GUIDE.md`、`memory/constitution.md`。
- **MCP / 工具**：`tools/`、`scripts/`（含 `setup_mcp_infrastructure.sh`）以及 `.devcontainer/`，支援 gcloud、Firestore、Slack… 等封裝。
- **服務骨架**：`analysis-service/`、`web-service/`、`tests/` 僅保留 Docker / requirements 與 `.gitkeep`，方便放入 Nooko 的室內設計自動化模組。

## 📝 起手式
1. 依 `DEVELOPMENT_GUIDELINES.md` 建立第一則 Session，紀錄初始化進度。
2. 安裝依賴：`poetry install` 或對各服務執行 `pip install -r requirements.txt`。
3. 檢閱 `QUICK_START_FOR_AI.md`、`docs/ai-collaboration-playbook.md`、`TOKEN_OPTIMIZATION_GUIDE.md`，熟悉 Spec Kit SOP 與 MCP 使用原則。
4. 在 `analysis-service/src`、`web-service/src`、`tests/unit` 中放入實際程式碼與測試，逐步擴充室內設計工作流程。

## 🧱 MCP 與 Automation
- 使用 `scripts/setup_mcp_infrastructure.sh` 建立必要 MCP server。
- 若需額外 API，參考 `docs/credential-management.md` 與 `TOKEN_OPTIMIZATION_GUIDE.md` 擴充。
- `docs/project-skeleton-export.md` 可協助在未來將此骨架複製到其他專案。

## 📦 部署提醒
- 根目錄保留原專案的 `cloudbuild*.yaml` 作為參考；目前尚未設定新的 Cloud Build 或 secrets，請依實際環境調整或改用其他 CI/CD。
- Docker 設定 (`Dockerfile*`) 可作為各服務的容器基礎，後續可依 Nooko 的需求增修。

## ✅ 下一步建議
1. 於 `specs/` 撰寫 Nooko 的需求與規格，維持 SDD 流程。
2. 在 `analysis-service` 與 `web-service` 建立室內設計 AI 模組、建立測試與監控工具。
3. 每個 session 結束前更新 `DEVELOPMENT_LOG.md` 與提供 Session Summary，以利未來協作者接續開發。

歡迎持續優化此骨架，打造專屬的室內設計自動化平台。🏡✨
