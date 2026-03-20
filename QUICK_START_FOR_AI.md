# AI 助理快速上手指南 (v4.0)

**目的**: 讓任何 AI 助理都能快速理解「報價防呆守衛」專案的最新方向，並遵循最佳實踐進行開發。
**閱讀時間**: 3 分鐘

---

## 專案速覽 (Project at a Glance)

- **產品定位 (Positioning)**:
  一個**「裝修報價單防呆助理」**（B2B 工具），為設計公司和統包商在發包前，自動揪出報價單中會導致「現場停工、做錯重來、嚴重漏項」的致命錯誤。

- **核心流程 (Core Flow)**:
  1. **輸入**: 使用者填寫現場條件 + 上傳報價單（Excel）
  2. **審核**: 系統自動執行三大防呆關卡（漏項/衝突/數量異常）
  3. **報告**: 產出紅黃綠燈防呆報告 + 具體修正建議
  4. **學習**: 老手透過回饋（確認/否決/調整）持續訓練系統

- **商業目標 (Business Goal)**:
  短期內部省錢避險 → 中期包裝為 SaaS 訂閱服務 → 長期建立業界發包標準。

- **目標用戶**: 室內設計公司、小型統包商、工程顧問（B2B）

---

## 技術棧 (Tech Stack)

**基於 [Better-T Stack](https://www.better-t-stack.dev/) 的 TypeScript 全端架構**

| 層級 | 技術 | 說明 |
|------|------|------|
| Runtime | Bun | TypeScript 原生、快速啟動 |
| Frontend | React + TanStack Router | File-based routing、type-safe |
| Backend | Hono | 輕量 API 框架 |
| API Layer | tRPC | 前後端 end-to-end type safety |
| Database | PostgreSQL (Neon) | Serverless、結構化報價資料 |
| ORM | Drizzle | Type-safe、SQL-like 語法 |
| Auth | Better-Auth | 支援 organization（多租戶） |
| UI | shadcn/ui + Tailwind CSS | 美觀、可客製 |
| AI | Google Gemini (via @google/genai) | 模糊推理、建議生成 |
| Monorepo | Turborepo | 管理 web + server + packages |
| Lint | Biome | 快速 lint + format |

---

## 核心架構原則

1. **規則引擎優先，AI 輔助**:
   - 確定性的工序連動、物理限制用「規則引擎」處理
   - 模糊判斷、建議文字用 Gemini AI 處理
   - 規則可透過老手回饋持續累積

2. **三大防呆關卡**:
   - **關卡 1 (漏項)**: 工序相依檢查 — 有 A 工項就必須有 B
   - **關卡 2 (衝突)**: 現場條件 × 建材/工法限制矩陣
   - **關卡 3 (異常)**: 數量與坪數的經驗比例檢查

3. **回饋迴路驅動成長**:
   - 老手確認 → 規則權重 +1
   - 老手否決 → 標記為例外
   - 老手調整 → 自動新增/修改規則

---

## 專案結構

```
nooko-quotation-guardian/         # Better-T Stack monorepo
├── apps/web/                     # React 前端
├── apps/server/                  # Hono + tRPC 後端
├── packages/shared/              # 共用型別
├── packages/construction-knowledge/  # 工程知識庫
└── specs/003-quotation-guardian/  # 規格文件
    ├── PRODUCT_BRIEF.md          # 產品定位與商業模式
    ├── plan.md                   # 技術架構與開發計畫
    └── schema-design.md          # 資料庫 schema 設計
```

---

## 核心開發原則

1. **統一語言**: 所有回覆、註解和日誌一律使用**繁體中文**
2. **Conventional Commits**: `feat:`, `fix:`, `docs:` 格式
3. **Type-safe 優先**: 善用 tRPC + Drizzle 的 end-to-end type safety
4. **測試**: 關鍵的規則引擎邏輯必須有單元測試

---

## 專案上下文快速查閱

- **產品定位?** → `specs/003-quotation-guardian/PRODUCT_BRIEF.md`
- **技術架構?** → `specs/003-quotation-guardian/plan.md`
- **DB Schema?** → `specs/003-quotation-guardian/schema-design.md`
- **舊版參考?** → `specs/002-interior-deco-ai/` (已棄用，部分知識保留)
- **工程知識?** → `analysis-service/src/agents/construction_translator.py` (待移植)

---

*文件版本: 4.0*
*上次更新: 2026-03-05*
*主要變更: 產品方向 pivot 為 B2B 報價防呆守衛，技術棧改為 Better-T Stack (TypeScript 全端)*
