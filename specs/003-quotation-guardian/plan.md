# 技術架構計畫 — Nooko 報價防呆守衛

> **版本**: 1.0
> **日期**: 2026-03-05
> **技術棧**: Better-T Stack

---

## 一、技術棧選型（Better-T Stack）

```bash
bun create better-t-stack@latest nooko-quotation-guardian \
  --runtime bun \
  --frontend tanstack-router \
  --backend hono \
  --api trpc \
  --database postgres \
  --orm drizzle \
  --auth better-auth \
  --addons turborepo biome \
  --db-setup neon
```

### 選型理由

| 技術 | 選擇 | 理由 |
|------|------|------|
| **Runtime** | Bun | TypeScript 原生、啟動快、內建 test runner |
| **Frontend** | React + TanStack Router | 生態成熟、file-based routing、type-safe |
| **Backend** | Hono | 輕量、邊緣運算友好、middleware 生態豐富 |
| **API** | tRPC | 前後端 type-safe，報價資料結構複雜時很有價值 |
| **Database** | PostgreSQL (Neon) | 報價是結構化關聯資料、Neon serverless 免管 infra |
| **ORM** | Drizzle | 輕量、type-safe、SQL-like，對計算邏輯更直覺 |
| **Auth** | Better-Auth | 內建、支援 organization/team（多租戶） |
| **Monorepo** | Turborepo | 管理 web + server + shared packages |
| **Lint** | Biome | 比 ESLint+Prettier 快 35x |

### 額外整合

| 需求 | 技術 | 說明 |
|------|------|------|
| **UI 元件** | shadcn/ui + Tailwind CSS 4 | 美觀、可客製、accessibility |
| **表格** | TanStack Table | 報價單需要強大的表格功能 |
| **檔案解析** | xlsx (SheetJS) | 解析 Excel 報價單 |
| **AI 推理** | Google Gemini API (via @google/genai) | 保留現有 Gemini 整合，改用 TS SDK |
| **即時通知** | SSE / WebSocket | 審核進度即時更新 |
| **PDF 產出** | @react-pdf/renderer | 產出防呆報告 PDF |

---

## 二、專案結構（Monorepo）

```
nooko-quotation-guardian/
├── .env                               # 環境變數（DB URL, Auth secrets）
├── package.json                       # Root workspace
├── tsconfig.json
├── turbo.json                         # Turborepo 設定
├── biome.json                         # Biome lint/format 設定
├── bunfig.toml                        # Bun 設定
│
├── apps/
│   └── web/                           # React + TanStack Router 前端 (Vite SPA)
│       ├── package.json
│       ├── vite.config.ts
│       ├── index.html
│       ├── components.json            # shadcn/ui 設定
│       └── src/
│           ├── main.tsx
│           ├── index.css
│           ├── routes/                # File-based routing (TanStack Router)
│           │   ├── __root.tsx
│           │   ├── index.tsx                    # Landing / Dashboard
│           │   ├── login.tsx                    # Better-Auth 登入頁
│           │   ├── dashboard.tsx                # Better-Auth 使用者頁
│           │   ├── projects/
│           │   │   ├── index.tsx                # 專案列表
│           │   │   └── $projectId/
│           │   │       ├── index.tsx            # 專案概覽
│           │   │       ├── upload.tsx           # 上傳報價單
│           │   │       ├── review.tsx           # 防呆審核結果
│           │   │       └── rules.tsx            # 防呆規則管理
│           │   └── settings/
│           │       ├── index.tsx                # 帳號設定
│           │       └── team.tsx                 # 團隊管理
│           ├── components/
│           │   ├── quotation/                   # 報價單相關元件
│           │   │   ├── QuotationTable.tsx       # 報價單表格（TanStack Table）
│           │   │   ├── UploadDropzone.tsx       # 檔案上傳區
│           │   │   └── ReviewReport.tsx         # 審核報告卡片
│           │   ├── rules/                       # 規則相關元件
│           │   │   ├── RuleCard.tsx
│           │   │   └── RuleFeedback.tsx         # ✅❌✏️ 回饋按鈕
│           │   ├── sign-in-form.tsx             # Better-Auth 登入表單
│           │   ├── sign-up-form.tsx             # Better-Auth 註冊表單
│           │   ├── user-menu.tsx                # Better-Auth 使用者選單
│           │   └── ui/                          # shadcn/ui 元件
│           ├── lib/
│           │   ├── auth-client.ts               # Better-Auth client
│           │   └── utils.ts
│           └── utils/
│               └── trpc.ts                      # tRPC client setup
│
├── server/                            # Hono 後端 (頂層 workspace)
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsdown.config.ts               # Build 設定
│   └── src/
│       ├── index.ts                    # Hono server entry point
│       └── services/                   # 業務邏輯服務
│           ├── excel-parser.ts         # Excel 報價單解析
│           ├── review-engine.ts        # 三大防呆關卡引擎
│           ├── rule-engine.ts          # 規則比對引擎
│           ├── gemini.ts               # Gemini AI 推理
│           └── quantity-estimator.ts   # 數量合理性估算
│
├── packages/
│   ├── api/                           # tRPC Router 定義
│   │   ├── package.json
│   │   └── src/
│   │       ├── index.ts               # tRPC app handler (Hono 整合)
│   │       ├── context.ts             # tRPC context
│   │       └── routers/
│   │           ├── index.ts           # Root router
│   │           ├── project.ts         # 專案 CRUD
│   │           ├── quotation.ts       # 報價單上傳/解析
│   │           ├── review.ts          # 防呆審核
│   │           ├── rule.ts            # 規則 CRUD
│   │           └── feedback.ts        # 老手回饋
│   │
│   ├── auth/                          # Better-Auth 伺服器設定
│   │   ├── package.json
│   │   └── src/
│   │       └── index.ts               # Auth configuration (Drizzle adapter)
│   │
│   ├── db/                            # Drizzle ORM + Schema
│   │   ├── package.json
│   │   ├── drizzle.config.ts          # Drizzle config for Postgres
│   │   └── src/
│   │       ├── index.ts               # Drizzle client (Neon serverless driver)
│   │       ├── seed.ts                # 種子資料（基礎防呆規則）
│   │       └── schema/
│   │           ├── index.ts           # Schema barrel export
│   │           ├── auth.ts            # Better-Auth 的 auth tables
│   │           ├── project.ts         # 專案、現場條件
│   │           ├── quotation.ts       # 報價單、工項
│   │           ├── review.ts          # 審核記錄、發現
│   │           ├── rule.ts            # 防呆規則
│   │           └── feedback.ts        # 老手回饋
│   │
│   ├── env/                           # 環境變數驗證
│   │   └── src/
│   │       ├── server.ts
│   │       └── web.ts
│   │
│   ├── config/                        # 共用 TypeScript config
│   │   └── tsconfig.base.json
│   │
│   └── construction-knowledge/        # 工程知識庫（從現有 Python 移植）
│       ├── package.json
│       └── src/
│           ├── dependencies.ts        # 工序相依關係
│           ├── site-constraints.ts    # 現場限制條件
│           ├── quantity-formulas.ts   # 數量計算公式
│           └── trade-mapping.ts       # 工種對應表
```

---

## 三、核心資料流

```
┌─────────────────────────────────────────────────────────────┐
│                        使用者操作                             │
│                                                             │
│  1. 填寫現場條件 ──→  2. 上傳報價單(Excel) ──→  3. 點擊「審核」│
└───────────┬─────────────────┬──────────────────┬────────────┘
            │                 │                  │
            ▼                 ▼                  ▼
┌───────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  site_conditions │  │  excel-parser.ts  │  │  review-engine.ts │
│  → DB 存儲      │  │  → 解析為結構化   │  │  → 執行三大關卡   │
│                 │  │    工項資料       │  │                  │
└───────────────┘  └──────────────────┘  └──────┬───────────┘
                                                 │
                          ┌──────────────────────┤
                          │                      │
                          ▼                      ▼
                 ┌─────────────────┐   ┌──────────────────┐
                 │  rule-engine.ts  │   │  gemini.ts       │
                 │  (確定性規則比對) │   │  (AI 模糊推理)   │
                 └────────┬────────┘   └────────┬─────────┘
                          │                      │
                          ▼                      ▼
                 ┌─────────────────────────────────────────┐
                 │           ReviewReport                   │
                 │  🔴 紅燈：致命漏項 (must fix)             │
                 │  🟡 黃燈：疑似異常 (should check)         │
                 │  🟢 綠燈：通過 (ok)                      │
                 │  📊 信心分數：85%                        │
                 └──────────────────┬──────────────────────┘
                                    │
                                    ▼
                 ┌─────────────────────────────────────────┐
                 │          老手回饋迴路                      │
                 │  ✅ 正確 → 規則權重 +1                    │
                 │  ❌ 誤報 → 標記例外                      │
                 │  ✏️ 調整 → 新增/修改規則                  │
                 └─────────────────────────────────────────┘
```

---

## 四、與現有程式碼的關係

### 保留並移植的資產

| 現有 Python 程式 | 新 TypeScript 對應 | 說明 |
|---|---|---|
| `construction_translator.py` 的 dependencies 概念 | `packages/construction-knowledge/dependencies.ts` | 工序相依關係是防呆關卡 1 的核心 |
| `ConstructionItem.risks_if_skip` | `packages/shared/types/rule.ts` | 轉為防呆規則的「後果描述」 |
| `_translate_tile_to_wood_floor()` 等範例 | `db/seed.ts` | 轉為初始規則種子資料 |
| `gemini_service.py` 的 Vertex AI 整合 | `services/gemini.ts` | 改用 `@google/genai` TS SDK |
| Firestore 的 project model | Drizzle PostgreSQL schema | 結構化資料更適合 SQL |

### 不保留的部分

| 現有程式 | 原因 |
|---|---|
| `client_manager_agent.py` | B2C 對話流程，新方向不需要 |
| `designer_agent.py` | 設計建議功能，不在 MVP scope |
| `image_generation_service.py` | 渲染圖功能，不在 MVP scope |
| `web-service/` React 前端 | 全部用 Better-T Stack 重建 |
| GCP Cloud Build/Run 部署 | 改用更簡單的部署方式（Vercel/Cloudflare） |

---

## 五、開發階段

### Phase 1：骨架建立（第 1 週）

- [ ] 用 Better-T Stack CLI 產生專案
- [ ] 設定 Neon PostgreSQL
- [ ] 建立 Drizzle schema 並 migrate
- [ ] Better-Auth 設定（email + password）
- [ ] 基本 CRUD：專案、報價單

### Phase 2：核心引擎（第 2-3 週）

- [ ] Excel 報價單解析器
- [ ] 現場條件輸入表單
- [ ] 關卡 1：工序連動檢查（規則引擎）
- [ ] 關卡 2：物理條件檢查
- [ ] 關卡 3：數量比例檢查
- [ ] 審核報告頁面（紅黃綠燈）

### Phase 3：AI 整合（第 3-4 週）

- [ ] Gemini API 整合（TS SDK）
- [ ] AI 輔助模糊推理（規則引擎不確定時）
- [ ] AI 產出修正建議文字

### Phase 4：回饋迴路（第 4-5 週）

- [ ] 老手回饋介面（✅❌✏️）
- [ ] 回饋 → 規則自動新增/調權
- [ ] 規則管理後台

### Phase 5：閉門測試（第 5-6 週）

- [ ] 10 份歷史報價單測試
- [ ] 調教 AI 與規則閾值
- [ ] 修正 false positive / false negative

---

## 六、部署方案

| 元件 | 平台 | 說明 |
|------|------|------|
| Web 前端 | Vercel | React SPA，自動 CI/CD |
| API 後端 | Vercel Serverless / Railway | Hono 支援多平台 |
| Database | Neon PostgreSQL | Serverless，自動 scaling |
| AI | Google Vertex AI (Gemini) | 直接 API call |
| 檔案儲存 | Vercel Blob / R2 | 上傳的 Excel 檔案 |
