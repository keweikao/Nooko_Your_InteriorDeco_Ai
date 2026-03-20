# Nooko 報價防呆守衛 — 系統設計規格

> 報價單開立系統 + 即時防呆守衛。設計師在系統內建立報價單，系統根據先驗知識庫即時比對規則，提醒遺漏或衝突。
>
> **注意**：本規格取代舊有的「上傳報價單 → 事後審查」方向。`specs/003-quotation-guardian/` 下的 `PRODUCT_BRIEF.md`、`schema-design.md`、`plan.md` 為舊版文件，以本規格為準。

## 1. 系統架構

```
┌──────────────────────────────────────────────────┐
│                   Frontend (React)                │
│  ┌─────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Stepper  │  │  報價表格     │  │  提醒面板    │ │
│  │ 施工進度  │  │ 工項/單位/數量│  │  防呆警告    │ │
│  └─────────┘  └──────────────┘  └──────────────┘ │
└──────────────────┬───────────────────────────────┘
                   │ tRPC
┌──────────────────▼───────────────────────────────┐
│                Backend (Hono + tRPC)              │
│  ┌──────────────┐  ┌───────────────────────────┐ │
│  │ CRUD API     │  │ Guardian Engine            │ │
│  │ 案件/報價單   │  │ ┌─────────┐ ┌───────────┐ │ │
│  │              │  │ │ 規則比對 │ │ Gemini API│ │ │
│  │              │  │ │ (確定性) │ │ (模糊推理)│ │ │
│  │              │  │ └─────────┘ └───────────┘ │ │
│  └──────────────┘  └───────────────────────────┘ │
└──────────────────┬───────────────────────────────┘
                   │ Drizzle ORM
┌──────────────────▼───────────────────────────────┐
│          PostgreSQL (Neon)                        │
│  案件 · 報價單 · 工項 · 規則 · 提醒紀錄 · 回饋   │
└──────────────────────────────────────────────────┘
```

### Guardian Engine 雙層檢查

1. **規則比對（確定性）** — 先驗知識庫的 If-Then 規則，毫秒級回應。
2. **Gemini API（模糊推理）** — 規則庫未覆蓋的情境，僅在最終掃描時呼叫。

### 觸發時機

- **填完一行工項** → 即時單項規則比對
- **切換工種** → 跨工種連動檢查（見 §3 跨工種檢查演算法）
- **全部完成** → 最終全面掃描（含 Gemini 模糊推理）

## 2. 使用流程

### Step 1 — 建立案件

輕量表單，收集影響規則選擇的物件資料：

| 欄位 | 說明 | 影響 |
|------|------|------|
| 案件名稱 | 自由命名 | 識別用 |
| 物件型態 | 住宅 / 商辦 | 決定載入哪套規則集 |
| 屋齡區間 | 0-5 / 5-10 / 10-20 / 20-30 / 30+ 年 | 住宅專用，影響水電、防水等規則 |
| 坪數 | 數字 | 數量合理性判斷依據 |
| 樓層 | 數字 | 搬運、吊車相關規則 |
| 有無電梯 | 是/否 | 搬運費規則 |

系統根據型態 + 屋齡自動載入對應規則集。

MVP 為單用戶系統，project 隸屬於登入用戶（`user_id`）。多租戶/團隊功能不在 MVP 範圍。

### Step 2 — 填寫報價單

三欄式介面，按施工順序逐工種填寫：

```
設計師操作                          系統行為
─────────                          ────────
選擇/進入工種 ──────────────→ 載入該工種規則
填入一行工項（名稱/單位/數量）──→ 即時比對規則庫
  ├─ 無對應規則 ────────────→ 直接 Pass（—）
  ├─ 規則通過 ──────────────→ 顯示 ✓
  └─ 觸發規則 ──────────────→ 右側面板跳出提醒（⚠）
設計師回應提醒
  ├─ 加入 ──────────────────→ 自動新增工項到對應工種
  └─ 忽略 ──────────────────→ 必填原因，紀錄回饋
點「下一工種」───────────────→ 檢查是否有未處理提醒
  ├─ 全部處理完 ────────────→ 放行，進入下一工種
  └─ 有未處理 ──────────────→ 提示需先處理（soft gate）
```

#### Soft Gate 定義

所有 status=pending 的 alert 必須被移至 accepted 或 ignored 後，「下一工種」按鈕才啟用。這不是硬性封鎖（設計師隨時可回到已完成工種編輯），但確保每個工種的防呆議題都被逐一回應。

設計師可自由回到已完成的工種繼續編輯。回到已完成工種時，該工種 status 從 completed 變回 editing。若編輯觸發新的 alert，需再次處理完畢才能離開。

### Step 3 — 最終掃描 & 匯出

- 跨工種連動檢查 + Gemini 模糊推理
- 全部處理後匯出 Excel

## 3. 規則引擎

### 規則結構

```
trigger:    觸發條件（什麼工項/情境會觸發）
condition:  前提條件（案件需符合什麼條件）
action:     建議動作（缺少什麼、該補什麼）
severity:   red（必要）/ yellow（建議）
scope:      residential / commercial / shared
age_tier:   適用屋齡區間（住宅專用，null = 全屋齡）
```

### 規則類型與 condition_json 結構

| 類型 | 說明 | 範例 | condition_json 結構 |
|------|------|------|---------------------|
| dependency | 有 A 必須有 B | 有拆除 → 須有垃圾清運 | `{"requires": {"trade": "拆除", "item_keywords": ["垃圾清運"]}}` |
| linked | A+B 時須有 C | 有防水施作 → 須有試水測試 | `{"requires": {"trade": "泥作", "item_keywords": ["試水測試"]}}` |
| condition | 案件條件觸發 | 屋齡 20+ 年 → 建議全室換線 | `{"site": {"age_tier_min": 20}}` |
| conflict | A 和 B 不應並存 | 矽酸鈣板 vs 氧化鎂板 | `{"conflicts_with": {"item_keywords": ["氧化鎂板"]}}` |
| quantity | 數量與坪數比對 | 垃圾清運：每 10 坪約 2 車 | `{"quantity_ratio": {"per_area": 10, "expected": 2, "unit": "車"}}` |

**衝突規則的 alert 行為**：觸發時提醒「A 與 B 不建議並存」，「加入」動作為移除衝突項，「忽略」照常需填原因。

### trigger_item_pattern 比對策略

使用關鍵字陣列比對。`trigger_item_pattern` 存放 JSON 字串陣列，例如 `["拆除磁磚", "拆除地磚", "磁磚打除"]`。工項名稱只要包含陣列中任一關鍵字即視為命中。

### 跨工種檢查演算法

切換工種時，系統執行：
1. 收集目前已填寫的所有工種的所有工項
2. 重新評估所有 scope 符合且 type 為 dependency 或 linked 的規則
3. 若發現新的未滿足依賴，產生 alert 歸屬到對應的 section

### 規則來源

- **MVP 內建**：PRIOR_KNOWLEDGE.md 中的確定性規則（已經設計師驗證）。
- **未來擴充**：設計師忽略提醒時填寫的原因 → 回饋迴路優化規則。

### 無規則即 Pass

工項若無對應規則，直接放行不檢查。只有命中規則庫的工項才觸發檢查。

## 4. 資料模型

### 屋齡區間定義

屋齡區間使用左閉右開區間：[0,5)、[5,10)、[10,20)、[20,30)、[30,∞)。

project 儲存 `age_tier` 為整數（該區間的下界值：0/5/10/20/30）。規則的 `age_tier_min` / `age_tier_max` 也是整數。比對邏輯：`age_tier_min <= project.age_tier < age_tier_max`（null 表示不限）。

### Schema

```
project (案件)
├── id, user_id
├── name, type (residential / commercial), age_tier (int), area, floor, has_elevator
├── status (draft / in_progress / completed)
├── created_at, updated_at
│
├── quotation (報價單) 1:1
│   ├── id, project_id
│   ├── created_at, updated_at, exported_at
│   │
│   ├── quotation_section (工種區段) 1:N
│   │   ├── id, quotation_id
│   │   ├── trade_code (見工種列表)
│   │   ├── sort_order (施工順序)
│   │   ├── status (pending / editing / completed)
│   │   │
│   │   └── quotation_item (工項) 1:N
│   │       ├── id, section_id
│   │       ├── name, unit, quantity
│   │       ├── source (manual / auto_added)
│   │       └── added_from_alert_id (nullable, 若由提醒加入)
│   │
│   └── alert (防呆提醒) 1:N
│       ├── id, quotation_id, section_id
│       ├── source (rule / gemini)
│       ├── rule_id (nullable, 規則觸發時對應的規則)
│       ├── trigger_item_id (哪個工項觸發)
│       ├── severity (red / yellow)
│       ├── message (提醒訊息文字)
│       ├── suggestion (建議動作描述)
│       ├── status (pending / accepted / ignored)
│       ├── ignore_reason (忽略原因, nullable)
│       ├── ai_confidence (nullable, Gemini 來源時的信心分數 0-1)
│       ├── ai_reasoning (nullable, Gemini 推理說明)
│       └── resolved_at
│
rule (規則庫)
├── id
├── type (dependency / linked / condition / conflict / quantity)
├── trigger_trade, trigger_item_pattern (JSON string array)
├── condition_json (JSON, 見 §3 各類型結構)
├── action_trade, action_item (建議加入的工項)
├── message_template (提醒訊息模板)
├── severity (red / yellow)
├── scope (residential / commercial / shared)
├── age_tier_min (nullable int), age_tier_max (nullable int)
└── active (boolean)
```

### 工種列表（13 工種，按施工順序）

| sort_order | trade_code | 顯示名稱 |
|------------|------------|----------|
| 1 | protection | 保護工程 |
| 2 | demolition | 拆除工程 |
| 3 | masonry | 泥作工程 |
| 4 | waterproof | 防水工程 |
| 5 | plumbing_electrical | 水電工程 |
| 6 | carpentry | 木作工程 |
| 7 | painting | 油漆工程 |
| 8 | wallpaper | 壁紙工程 |
| 9 | flooring | 地板工程 |
| 10 | cabinet_kitchen | 系統櫃/廚具 |
| 11 | hvac | 空調工程 |
| 12 | door_window | 門窗工程 |
| 13 | cleaning | 清潔工程 |

注意：衛浴設備通常歸入泥作或水電，不獨立成工種。設計師可在任何工種中自由新增工項。

### Edge Cases

- **刪除已觸發 alert 的工項**：對應的 alert 自動標記為 accepted（來源已移除，提醒失效）。
- **刪除由 alert 自動加入的工項**：該 alert 回到 pending 狀態，重新提醒。
- **修改案件資料（如屋齡）**：觸發全面重新評估，新增/移除不適用的 alert。

## 5. 前端元件結構

```
App
├── ProjectCreatePage (建立案件表單)
│   └── SiteConditionForm (物件資料：型態/屋齡/坪數/樓層/電梯)
│
├── QuotationPage (三欄主畫面)
│   ├── TradeStepper (左欄 - 施工進度)
│   │   ├── StepperItem × 13 (每個工種一步)
│   │   │   ├── 狀態：completed ✓ / current (editing) / pending
│   │   │   └── 未處理提醒 badge
│   │   └── ProgressBar (整體進度)
│   │
│   ├── ItemTable (中欄 - 工項表格)
│   │   ├── Header: 工項名稱 / 單位 / 數量 / 狀態
│   │   ├── ItemRow × N
│   │   │   ├── 狀態欄：✓ pass / ⚠ alert / — no rule
│   │   │   └── 觸發提醒的行有視覺標記
│   │   ├── AddItemRow (+ 新增工項)
│   │   └── SectionNav (← 上一工種 / 下一工種 →)
│   │       └── Soft gate: 有 pending alert 時下一步帶 badge 且 disabled
│   │
│   └── AlertPanel (右欄 - 防呆提醒)
│       ├── ActiveAlerts (待處理)
│       │   └── AlertCard × N
│       │       ├── severity + message + 觸發來源
│       │       └── 加入 / 忽略 按鈕
│       ├── ResolvedAlerts (已處理，灰色)
│       └── GateStatus (本工種狀態摘要)
│
├── FinalScanPage (最終掃描)
│   ├── 跨工種連動檢查結果
│   ├── Gemini 模糊推理結果
│   └── 全部處理後 → 匯出按鈕
│
└── ExportPage (匯出 Excel)
```

### 技術選型

- **shadcn/ui** — 基礎元件
- **TanStack Table** — 工項表格
- **TanStack Router** — 頁面路由
- **tRPC mutation** — 工項填入後即時觸發規則比對

### 設計風格

簡約設計。低飽和色調、充足留白、清晰視覺層次。避免過度裝飾，專注功能性。

## 6. MVP 範圍

### 包含

- 案件建立（住宅 + 商辦）
- 住宅屋齡分級（[0,5) / [5,10) / [10,20) / [20,30) / [30,∞)）
- 報價單開立（13 工種 stepper + 工項表格）
- 即時規則比對（確定性規則）
- 最終掃描（含 Gemini 模糊推理）
- 防呆提醒（加入 / 忽略+原因）
- Soft gate（所有 pending alert 需處理完才能進下一工種）
- 匯出 Excel
- 單用戶認證（Better-Auth）

### 不含

- 單價 / 小計 / 毛利率（加價模組）
- 診所 / 餐飲 / 零售等其他物件型態
- 團隊協作 / 權限管理 / 多租戶
- LINE / Slack 機器人
- 歷史報價單比對
- PDF 匯出

## 7. 技術堆疊

- **Runtime**: Bun
- **Frontend**: React + TanStack Router + shadcn/ui + TanStack Table
- **Backend**: Hono + tRPC
- **ORM**: Drizzle ORM
- **Database**: PostgreSQL (Neon)
- **Auth**: Better-Auth
- **AI**: Google Gemini API（最終掃描模糊推理）
- **Monorepo**: Turborepo
- **Linter**: Biome
