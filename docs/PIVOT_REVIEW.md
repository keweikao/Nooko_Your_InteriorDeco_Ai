# Pivot Review：從消費者工具轉型為設計公司/統包商報價系統

> 審查日期：2026-03-04
> 目標：盤點現有專案中哪些模組可保留、需改造、或應移除

---

## 一、現況概覽

目前專案 **HouseIQ** 是一個面向**一般裝潢消費者**的 AI 夥伴，核心流程為：

1. 消費者上傳報價單（PDF/Excel/圖片）
2. AI 對話引導蒐集裝修需求（5 階段式問卷）
3. AI 分析報價單風險、產出工程規格建議
4. 串接統包商 Agent 產出新報價 + 設計師 Agent 產出渲染圖
5. 消費者預約免費到府丈量

**Pivot 後的目標客戶**：設計公司、統包商（B2B 工具）
**核心用途**：協助專業人員快速開立、編輯、管理報價單

---

## 二、保留程度分類

### ✅ 可直接保留（核心價值仍適用）

| 模組 | 檔案位置 | 保留原因 |
|------|----------|----------|
| **FastAPI 應用骨架** | `analysis-service/src/main.py` | CORS、路由架構、健康檢查端點，與業務邏輯無關，可直接沿用 |
| **BaseAgent 抽象類** | `analysis-service/src/agents/base_agent.py` | 通用 Agent 介面，pivot 後的報價產生 Agent 仍可繼承 |
| **Gemini/Vertex AI 整合** | `analysis-service/src/services/gemini_service.py` | LLM 串接層（model init、streaming、content building）是核心能力，pivot 後用來協助智慧報價仍然需要 |
| **Firestore 對話服務** | `analysis-service/src/services/conversation_service.py` | 對話持久化、訊息存取、事件日誌機制完全通用，改名為「專案對話紀錄」即可 |
| **Database Service（雙模式）** | `analysis-service/src/services/database_service.py` | Mock/Firestore 雙模式設計良好，資料模型改一下就能繼續用 |
| **Secret Service** | `analysis-service/src/services/secret_service.py` | 密鑰管理與業務邏輯無關 |
| **PDF 產出服務** | `analysis-service/src/services/pdf_service.py` | 報價單 PDF 匯出是 pivot 後的核心功能之一，架構保留、內容模板需重寫 |
| **檔案上傳 API** | `projects.py` 中的 `/upload` 端點 | 統包商/設計公司也需要上傳既有報價單或平面圖，GCS + Pub/Sub 流程保留 |
| **SSE 串流架構** | `projects.py` 中的 `/message-stream` | 即時對話串流機制通用，pivot 後用來做「AI 報價助理」對話 |
| **GCP 部署配置** | `Dockerfile`, `cloudbuild.yaml` | 部署管線與業務邏輯無關 |
| **Web 前端基礎設施** | `web-service/` 中的 Vite + React + Tailwind 配置 | 技術選型通用 |
| **UI 基礎元件** | `web-service/src/components/ui/*` | button, card, input, tabs, badge 等 shadcn/ui 元件完全通用 |
| **Spec Tracking 機制** | `analysis-service/src/services/spec_tracking.py` | 階段式進度追蹤的**架構設計**（SpecField、evaluate、merge）非常好，改欄位定義即可重用 |

### 🔧 需要改造（架構可用，業務邏輯需重寫）

| 模組 | 檔案位置 | 改造方向 |
|------|----------|----------|
| **資料模型 (Project/Quote/LineItem)** | `analysis-service/src/models/project.py` | `LineItem`、`Quote` 模型結構非常好，**直接就是報價單核心模型**。需要擴充：客戶資訊、工程地址、付款條件、保固條款、報價有效期等欄位。`ExtractedSpecifications` 需從「消費者需求」改為「工程項目規格」 |
| **ContractorAgent（統包商 Agent）** | `analysis-service/src/agents/contractor_agent.py` | 目前是「根據 brief 自動產生報價」，pivot 後改為「協助統包商編輯/優化/補全報價」，從「產出報價」變成「報價助理」 |
| **Gemini System Prompt** | `gemini_service.py` 中的 `_build_dynamic_system_prompt()` | 目前 prompt 是以消費者顧問角色設計，pivot 後需改為「報價編輯助理」角色，協助專業人員：補漏項、計算數量、建議單價範圍、風險提示 |
| **SpecTracker 欄位定義** | `spec_tracking.py` 中的 `SPEC_FIELDS` | 5 階段從「消費者需求蒐集」改為「報價單建立流程」，例如：客戶資訊 → 工程範圍 → 工項明細 → 材料規格 → 條款與條件 |
| **ConversationUI** | `web-service/src/components/ConversationUI.jsx` | 對話介面保留，但使用情境從「消費者問卷」變成「報價編輯對話」，需調整 UI 文案和互動流程 |
| **MessageList / MessageInput** | `web-service/src/components/conversation/*` | 對話元件通用，微調樣式即可 |
| **FileUpload** | `web-service/src/components/FileUpload.jsx` | 上傳功能保留，說明文字從「上傳報價單供分析」改為「匯入既有報價單或平面圖」 |
| **FinalResult** | `web-service/src/components/FinalResult.jsx` | 改造為「報價單預覽/匯出」頁面 |
| **QuoteTable 元件** | `web-service/src/components/results/QuoteTable.jsx` | 報價表格是**核心 UI**，需要從「唯讀展示」改造為「可編輯表格」，加入新增/刪除行、單價修改、小計自動計算 |
| **App.jsx 主流程** | `web-service/src/App.jsx` | 步驟流程從 welcome→upload→questionnaire→results→booking 改為 login→project_list→edit_quote→preview→export |
| **ConstructionTranslator** | `analysis-service/src/agents/construction_translator.py` | 工程項目翻譯規則庫（磁磚改木地板、浴室整修、廚房整修等）中的**工項拆解邏輯和專業知識非常有價值**，pivot 後可作為「智慧工項建議引擎」，當統包商輸入粗略項目時，AI 自動建議應包含的子項目 |

### ❌ 應移除或大幅精簡

| 模組 | 檔案位置 | 移除原因 |
|------|----------|----------|
| **ClientManagerAgentV2（消費者問卷系統）** | `analysis-service/src/agents/client_manager_v2.py` | 整個 30 題問卷（風格喜好、生活需求、家庭成員等）是純消費者導向設計，專業人員不需要這些。但其中的**條件式問題邏輯**（`show_if`、`triggers_follow_up`）架構可參考 |
| **ClientManagerAgent V1** | `analysis-service/src/agents/client_manager_agent.py`, `client_manager.py` | 舊版客戶經理，已無用 |
| **DesignerAgent（設計師 Agent）** | `analysis-service/src/agents/designer_agent.py` | 產出渲染圖功能不是報價系統所需。若未來有「報價附帶 3D 示意圖」需求可再考慮 |
| **Image Generation Service** | `analysis-service/src/services/image_generation_service.py` | 圖片生成與報價系統無關 |
| **BookingForm（預約表單）** | `web-service/src/components/BookingForm.jsx` | 「到府丈量預約」是消費者功能，B2B 不需要 |
| **FeedbackFlow** | `web-service/src/components/FeedbackFlow.jsx` | 消費者滿意度回饋，B2B 情境不適用 |
| **AnalysisSection** | `web-service/src/components/AnalysisSection.jsx` | 「AI 正在分析中」的等待動畫頁面，B2B 流程不同 |
| **InteractiveQuestionnaire** | `web-service/src/components/InteractiveQuestionnaire.jsx` | 消費者互動問卷 UI |
| **StyleGuide / ComponentGallery** | `web-service/src/components/StyleGuide.jsx`, `ComponentGallery.jsx` | 展示用，不進入產品 |
| **Retro UI 元件** | `web-service/src/components/retro/*` | 裝飾性元件，B2B 不需要 |
| **MagicUI 元件** | `web-service/src/components/magicui/*` | 花俏視覺效果，B2B 工具偏向功能導向 |
| **Booking 相關 API** | `projects.py` 中的 `/book` 端點 | 預約丈量是消費者功能 |
| **Feedback 相關 API** | `projects.py` 中的 `/feedback` 端點 | 消費者回饋 |
| **V1 問卷 API** | `/conversation/start`, `/conversation/answer` | 舊版問卷流程 |
| **消費者導向歡迎訊息** | 散布於 `projects.py` 各處 | 「HouseIQ 裝潢 AI 夥伴」等文案需全面更換 |

---

## 三、Pivot 後的核心模組建議

### 新的使用者流程

```
設計公司/統包商登入
  → 建立新報價專案（填寫客戶名稱、地址、工程概述）
  → 選擇建立方式：
     a) 匯入既有報價單（PDF/Excel）→ AI 解析成結構化資料
     b) 從空白開始 → AI 對話引導建立工項
     c) 從範本開始 → 選擇常見工程範本
  → 編輯報價明細（可編輯表格 + AI 助理即時建議）
  → 預覽 → 匯出 PDF / Excel
  → 管理歷史報價（列表、搜尋、複製）
```

### 需要新增的模組

| 新模組 | 說明 |
|--------|------|
| **使用者認證系統** | 帳號管理、公司資料、多使用者支援 |
| **報價單 CRUD API** | 建立、讀取、更新、刪除報價單 |
| **報價單解析服務** | 上傳 PDF/Excel → 透過 AI 解析成結構化 LineItem |
| **報價範本系統** | 常見工程類型的預設報價範本 |
| **可編輯報價表格 UI** | 行內編輯、拖拉排序、自動計算小計/總計 |
| **報價單匯出服務** | 客製化 PDF 模板（含公司 Logo、條款）、Excel 匯出 |
| **專案列表/管理頁面** | 歷史報價搜尋、篩選、複製建立 |
| **AI 報價助理** | 基於 Gemini，提供工項建議、單價參考、風險提示 |

---

## 四、可保留資產的價值估算

| 類別 | 預估可保留比例 | 說明 |
|------|:---:|------|
| 基礎設施（GCP、Docker、CI/CD） | **90%** | 幾乎全部保留 |
| 後端框架（FastAPI + 路由架構） | **70%** | 路由需增刪，但骨架不變 |
| 資料庫層（Firestore + 雙模式） | **80%** | Schema 改動，服務層保留 |
| LLM 整合層（Gemini streaming） | **75%** | 串接邏輯保留，prompt 全面重寫 |
| 領域知識（工項翻譯、施工順序） | **60%** | `ConstructionTranslator` 中的工程知識是寶藏，需要從「解釋給消費者聽」改為「輔助專業人員補全工項」 |
| 資料模型 | **50%** | `LineItem`/`Quote` 直接可用，其餘需重建 |
| 前端基礎設施 | **60%** | Vite + React + Tailwind + UI 元件保留，頁面/流程需重做 |
| 對話系統 | **55%** | SSE + 對話持久化保留，對話邏輯需重寫 |

**整體可保留比例估計：約 50-60%**

---

## 五、建議 Pivot 優先順序

### Phase 1：核心報價功能（MVP）
1. 重新定義資料模型（Quote、LineItem 擴充、新增 Company/User）
2. 建立報價單 CRUD API
3. 可編輯報價表格 UI
4. PDF 匯出（基礎版）

### Phase 2：AI 智慧功能
5. 報價單解析（上傳 → 結構化）
6. AI 報價助理對話（基於現有 Gemini + SSE 改造）
7. 智慧工項建議（基於 ConstructionTranslator 改造）

### Phase 3：協作與管理
8. 使用者認證 + 公司帳號
9. 報價範本系統
10. 歷史報價管理 + 搜尋

---

## 六、結論

這個專案在 pivot 過程中有相當程度的資產可以保留，特別是：

1. **基礎設施層**（GCP 部署、Docker、FastAPI 骨架）幾乎完全可重用
2. **LLM 整合層**（Gemini streaming + Firestore 對話持久化）是核心技術能力
3. **領域知識**（`ConstructionTranslator` 中的工程工項拆解邏輯）在 B2B 場景中價值更高
4. **`LineItem` / `Quote` 資料模型**恰好就是報價系統的核心

主要需要新增的是：使用者認證、可編輯報價表格 UI、報價單解析、以及面向專業人員的 prompt 設計。消費者導向的問卷系統和預約功能則可以移除。
