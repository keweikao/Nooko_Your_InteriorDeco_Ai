# Drizzle Schema 設計 — 報價防呆守衛

> **版本**: 1.0
> **日期**: 2026-03-05

---

## 資料模型總覽

```
Organization (公司/團隊)
 └─ User (使用者，多對多)
 └─ Project (專案/案場)
     ├─ SiteCondition (現場條件)
     ├─ Quotation (報價單)
     │   └─ QuotationItem (報價工項)
     └─ Review (審核記錄)
         └─ ReviewFinding (審核發現)
             └─ Feedback (老手回饋)

Rule (防呆規則，公司層級)
```

---

## Schema 定義（Drizzle TypeScript）

```typescript
// ============================================
// schema.ts - Drizzle ORM Schema
// ============================================

import { pgTable, text, integer, boolean, timestamp, real,
         pgEnum, jsonb, uuid, primaryKey } from "drizzle-orm/pg-core";

// ---- Enums ----

export const severityEnum = pgEnum("severity", ["critical", "warning", "info"]);
export const reviewStatusEnum = pgEnum("review_status", ["pending", "processing", "completed", "failed"]);
export const feedbackTypeEnum = pgEnum("feedback_type", ["confirm", "dismiss", "adjust"]);
export const ruleSourceEnum = pgEnum("rule_source", ["system", "ai_suggested", "expert_feedback", "manual"]);
export const tradeCategoryEnum = pgEnum("trade_category", [
  "demolition",       // 拆除
  "masonry",          // 泥作
  "plumbing",         // 水電
  "carpentry",        // 木作
  "painting",         // 油漆
  "flooring",         // 地板
  "ceiling",          // 天花板
  "cabinet",          // 系統櫃/廚具
  "hvac",             // 空調
  "window_door",      // 門窗
  "waterproofing",    // 防水
  "cleaning",         // 清潔
  "transport",        // 搬運
  "other"             // 其他
]);

// ---- Organization & Users (Better-Auth 擴展) ----

export const organization = pgTable("organization", {
  id: uuid("id").defaultRandom().primaryKey(),
  name: text("name").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Note: Better-Auth 會自動建立 user, session, account 表
// 以下是擴展欄位
export const userProfile = pgTable("user_profile", {
  userId: text("user_id").primaryKey(),  // 關聯到 Better-Auth user
  organizationId: uuid("organization_id").references(() => organization.id),
  role: text("role").default("member"),  // "owner" | "admin" | "member"
  displayName: text("display_name"),
  experienceYears: integer("experience_years"),  // 經驗年數，影響回饋權重
});

// ---- Project (專案/案場) ----

export const project = pgTable("project", {
  id: uuid("id").defaultRandom().primaryKey(),
  organizationId: uuid("organization_id").references(() => organization.id).notNull(),
  name: text("name").notNull(),            // 案場名稱，如「信義區張宅」
  address: text("address"),                 // 地址
  description: text("description"),
  createdBy: text("created_by").notNull(),  // user id
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

// ---- Site Condition (現場條件) ----

export const siteCondition = pgTable("site_condition", {
  id: uuid("id").defaultRandom().primaryKey(),
  projectId: uuid("project_id").references(() => project.id).notNull(),

  // 基本資訊
  totalArea: real("total_area"),                    // 室內總坪數
  floorLevel: integer("floor_level"),               // 樓層
  hasElevator: boolean("has_elevator"),              // 有無電梯
  buildingType: text("building_type"),               // 公寓/透天/大樓/老屋
  buildingAge: integer("building_age"),              // 屋齡（年）
  ceilingHeight: real("ceiling_height"),             // 天花板高度（cm）

  // 特殊條件
  hasMoistureIssue: boolean("has_moisture_issue").default(false),
  hasLeakIssue: boolean("has_leak_issue").default(false),
  isOccupied: boolean("is_occupied").default(false), // 施工期間是否有人住
  hasParking: boolean("has_parking").default(true),  // 工程車是否可停
  specialNotes: text("special_notes"),               // 其他特殊條件

  // 格局資訊（JSON，彈性結構）
  rooms: jsonb("rooms"),  // [{ type: "living", area: 8 }, { type: "bedroom", area: 5 }]

  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

// ---- Quotation (報價單) ----

export const quotation = pgTable("quotation", {
  id: uuid("id").defaultRandom().primaryKey(),
  projectId: uuid("project_id").references(() => project.id).notNull(),
  fileName: text("file_name"),                      // 原始檔名
  fileUrl: text("file_url"),                        // 儲存路徑
  uploadedBy: text("uploaded_by").notNull(),
  uploadedAt: timestamp("uploaded_at").defaultNow().notNull(),
  parsedAt: timestamp("parsed_at"),                 // 解析完成時間
  totalAmount: real("total_amount"),                 // 報價總金額
  itemCount: integer("item_count"),                  // 工項數量
  rawData: jsonb("raw_data"),                        // 原始解析資料（備份）
});

// ---- Quotation Item (報價工項) ----

export const quotationItem = pgTable("quotation_item", {
  id: uuid("id").defaultRandom().primaryKey(),
  quotationId: uuid("quotation_id").references(() => quotation.id).notNull(),

  // 工項資訊
  category: tradeCategoryEnum("category"),           // 工種分類
  itemName: text("item_name").notNull(),             // 工項名稱
  unit: text("unit"),                                // 單位（坪/式/組/個）
  quantity: real("quantity"),                         // 數量
  unitPrice: real("unit_price"),                     // 單價
  totalPrice: real("total_price"),                   // 小計
  specification: text("specification"),              // 規格說明
  notes: text("notes"),                              // 備註

  // 解析元資料
  originalRow: integer("original_row"),              // Excel 原始行號
  confidence: real("confidence"),                    // AI 解析信心度 (0-1)
  sortOrder: integer("sort_order"),                  // 排序
});

// ---- Review (審核記錄) ----

export const review = pgTable("review", {
  id: uuid("id").defaultRandom().primaryKey(),
  quotationId: uuid("quotation_id").references(() => quotation.id).notNull(),
  status: reviewStatusEnum("status").default("pending"),
  triggeredBy: text("triggered_by").notNull(),       // user id

  // 審核結果摘要
  overallScore: real("overall_score"),                // 整體信心分數 (0-100)
  criticalCount: integer("critical_count").default(0),  // 紅燈數量
  warningCount: integer("warning_count").default(0),    // 黃燈數量
  passCount: integer("pass_count").default(0),          // 綠燈數量

  startedAt: timestamp("started_at"),
  completedAt: timestamp("completed_at"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// ---- Review Finding (審核發現) ----

export const reviewFinding = pgTable("review_finding", {
  id: uuid("id").defaultRandom().primaryKey(),
  reviewId: uuid("review_id").references(() => review.id).notNull(),

  // 關卡資訊
  checkType: text("check_type").notNull(),           // "dependency" | "site_conflict" | "quantity_anomaly"
  severity: severityEnum("severity").notNull(),

  // 發現內容
  title: text("title").notNull(),                    // 簡短標題
  description: text("description").notNull(),         // 詳細說明
  suggestion: text("suggestion"),                     // 修正建議

  // 關聯的工項
  relatedItemIds: jsonb("related_item_ids"),          // quotation_item ids
  matchedRuleId: uuid("matched_rule_id"),             // 觸發的規則 id

  // AI 推理資訊
  aiConfidence: real("ai_confidence"),                // AI 信心度 (0-1)
  aiReasoning: text("ai_reasoning"),                  // AI 推理過程

  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// ---- Feedback (老手回饋) ----

export const feedback = pgTable("feedback", {
  id: uuid("id").defaultRandom().primaryKey(),
  findingId: uuid("finding_id").references(() => reviewFinding.id).notNull(),
  userId: text("user_id").notNull(),

  type: feedbackTypeEnum("type").notNull(),           // confirm | dismiss | adjust
  adjustedContent: text("adjusted_content"),           // 如果是 adjust，調整後的內容
  notes: text("notes"),                                // 備註說明

  // 回饋後的動作
  createdRuleId: uuid("created_rule_id"),              // 如果產生了新規則
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// ---- Rule (防呆規則) ----

export const rule = pgTable("rule", {
  id: uuid("id").defaultRandom().primaryKey(),
  organizationId: uuid("organization_id").references(() => organization.id),  // null = 全域規則

  // 規則基本資訊
  name: text("name").notNull(),                       // 規則名稱
  description: text("description"),
  checkType: text("check_type").notNull(),            // "dependency" | "site_conflict" | "quantity_anomaly"
  severity: severityEnum("severity").notNull(),
  source: ruleSourceEnum("source").notNull(),

  // 規則條件（JSON，彈性結構）
  // 關卡 1 範例: { "if_has": "全熱交換器", "must_have": "洗洞", "in_category": ["masonry", "plumbing"] }
  // 關卡 2 範例: { "if_condition": { "has_elevator": false, "floor_level": { "gte": 3 } }, "if_item_matches": "大板磚", "must_have": "吊車" }
  // 關卡 3 範例: { "item_category": "painting", "ratio_to_total_area": { "min": 2.5, "max": 4.0 }, "unit": "坪" }
  condition: jsonb("condition").notNull(),

  // 觸發時的訊息模板
  messageTemplate: text("message_template").notNull(), // 支援 {{變數}} 插值
  suggestionTemplate: text("suggestion_template"),

  // 統計與權重
  weight: real("weight").default(1.0),                 // 權重（回饋越多越高）
  triggerCount: integer("trigger_count").default(0),   // 被觸發次數
  confirmCount: integer("confirm_count").default(0),   // 被確認次數
  dismissCount: integer("dismiss_count").default(0),   // 被否決次數

  isActive: boolean("is_active").default(true),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});
```

---

## 關聯圖 (ER Diagram)

```
┌──────────────┐     ┌──────────────┐
│ organization │◄────┤ userProfile  │
└──────┬───────┘     └──────────────┘
       │
       │ 1:N
       ▼
┌──────────────┐     ┌───────────────────┐
│   project    │────►│  siteCondition    │
└──────┬───────┘     └───────────────────┘
       │
       │ 1:N
       ▼
┌──────────────┐
│  quotation   │
└──────┬───────┘
       │
       ├─── 1:N ──►┌──────────────────┐
       │            │  quotationItem   │
       │            └──────────────────┘
       │
       └─── 1:N ──►┌──────────────┐
                    │    review    │
                    └──────┬───────┘
                           │
                           │ 1:N
                           ▼
                    ┌──────────────────┐
                    │  reviewFinding   │
                    └──────┬───────────┘
                           │
                           │ 1:N
                           ▼
                    ┌──────────────┐
                    │   feedback   │
                    └──────────────┘

┌──────────────┐ (獨立)
│     rule     │
└──────────────┘
```

---

## 種子資料範例（防呆規則）

從現有 `construction_translator.py` 萃取的初始規則：

```typescript
// seed.ts - 初始防呆規則
const seedRules = [
  // === 關卡 1：工序連動 ===
  {
    name: "全熱交換器必須搭配洗洞",
    checkType: "dependency",
    severity: "critical",
    source: "system",
    condition: {
      if_has: ["全熱交換器", "全熱交換"],
      must_have_any: ["洗洞", "鑽孔", "穿孔"],
      in_category: ["masonry", "plumbing"]
    },
    messageTemplate: "報價有「{{matched_item}}」，但找不到對應的洗洞/鑽孔工項。全熱交換器需要在外牆鑽孔才能安裝進排氣管。",
    suggestionTemplate: "請在泥作或水電工項中加入「洗洞」，通常需要 2-4 個孔（依機型而定）。"
  },
  {
    name: "拆除磁磚必須搭配地面整平",
    checkType: "dependency",
    severity: "critical",
    source: "system",
    condition: {
      if_has: ["拆除磁磚", "拆除地磚"],
      must_have_any: ["地面整平", "泥作整平", "自平水泥"],
      in_category: ["masonry"]
    },
    messageTemplate: "報價有「拆除磁磚」，但找不到「地面整平」工項。拆除後地面會有高低差，必須整平才能進行後續施工。",
    suggestionTemplate: "請在泥作中加入「地面整平」，視面積估算約 {{area}} 坪。"
  },
  {
    name: "浴室拆除必須搭配防水工程",
    checkType: "dependency",
    severity: "critical",
    source: "system",
    condition: {
      if_has: ["浴室拆除", "衛浴拆除"],
      must_have_any: ["防水工程", "防水層", "防水施工"],
    },
    messageTemplate: "報價有浴室拆除，但找不到防水工程。浴室必須重做防水層並做 48 小時試水測試。",
    suggestionTemplate: "請加入「防水工程（含 48 小時試水測試）」，這是浴室整修最重要的工項。"
  },

  // === 關卡 2：現場衝突 ===
  {
    name: "高樓無電梯大型建材需搬運費",
    checkType: "site_conflict",
    severity: "warning",
    source: "system",
    condition: {
      if_site: { has_elevator: false, floor_level: { gte: 3 } },
      if_item_matches: ["大板磚", "240", "120x240", "80x160"],
      must_have_any: ["吊車", "吊掛", "特殊搬運", "搬運工資"]
    },
    messageTemplate: "案場為無電梯 {{floor_level}} 樓，報價含大型建材「{{matched_item}}」，但未列搬運費用。",
    suggestionTemplate: "請加入「特殊搬運工資」或「吊車費用」。無電梯高樓搬運大板磚需要額外人力或吊掛設備。"
  },

  // === 關卡 3：數量異常 ===
  {
    name: "油漆面積應為地坪 2.5-4 倍",
    checkType: "quantity_anomaly",
    severity: "warning",
    source: "system",
    condition: {
      item_category: "painting",
      ratio_to_total_area: { min: 2.5, max: 4.0 },
      unit: "坪"
    },
    messageTemplate: "室內總坪數 {{total_area}} 坪，油漆報 {{item_quantity}} 坪（比例 {{ratio}}x）。正常應為地坪的 2.5-4 倍（含牆面、天花板）。",
    suggestionTemplate: "建議重新計算油漆面積。{{total_area}} 坪空間的油漆面積通常約 {{expected_min}}-{{expected_max}} 坪。"
  }
];
```
