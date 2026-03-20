# Nooko 報價防呆守衛 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a quotation creation system with real-time guardian alerts for Taiwan renovation designers.

**Architecture:** Better-T Stack monorepo — React frontend with three-column layout (stepper / table / alert panel), Hono+tRPC backend with Guardian Engine (rule matching + Gemini fuzzy reasoning), Drizzle ORM on PostgreSQL (Neon). The quotation guardian app is scaffolded as a separate monorepo `nooko-quotation-guardian/` inside the project root.

**Tech Stack:** Bun, React, TanStack Router, TanStack Table, shadcn/ui, Hono, tRPC, Drizzle ORM, PostgreSQL (Neon), Better-Auth, Google Gemini API, Turborepo, Biome

**Spec:** `docs/superpowers/specs/2026-03-20-quotation-guardian-design.md`

---

## File Structure

### Monorepo Root (`nooko-quotation-guardian/`)

```
nooko-quotation-guardian/
├── package.json              # Root workspace config
├── turbo.json                # Turborepo pipeline
├── biome.json                # Biome lint/format
├── .env                      # DB URL, auth secret, Gemini API key
├── .env.example
│
├── apps/
│   └── web/                  # React frontend (Vite SPA)
│       ├── package.json
│       ├── vite.config.ts
│       ├── components.json   # shadcn/ui config
│       └── src/
│           ├── main.tsx
│           ├── index.css
│           ├── routes/
│           │   ├── __root.tsx
│           │   ├── index.tsx                    # Redirect to /projects
│           │   ├── login.tsx
│           │   ├── projects/
│           │   │   ├── index.tsx                # Project list
│           │   │   └── new.tsx                  # Create project form
│           │   └── quotation/
│           │       └── $projectId.tsx           # Three-column quotation page
│           ├── components/
│           │   ├── quotation/
│           │   │   ├── TradeStepper.tsx
│           │   │   ├── StepperItem.tsx
│           │   │   ├── ItemTable.tsx
│           │   │   ├── ItemRow.tsx
│           │   │   ├── AddItemRow.tsx
│           │   │   ├── SectionNav.tsx
│           │   │   ├── AlertPanel.tsx
│           │   │   ├── AlertCard.tsx
│           │   │   └── GateStatus.tsx
│           │   ├── project/
│           │   │   ├── ProjectCard.tsx
│           │   │   └── SiteConditionForm.tsx
│           │   ├── final-scan/
│           │   │   └── FinalScanView.tsx
│           │   └── ui/                          # shadcn/ui components
│           ├── lib/
│           │   ├── trpc.ts                      # tRPC client
│           │   ├── auth-client.ts               # Better-Auth client
│           │   └── utils.ts                     # cn() helper
│           └── constants/
│               └── trades.ts                    # 13 trade codes + display names
│
├── server/                   # Hono backend
│   ├── package.json
│   └── src/
│       ├── index.ts          # Hono entry + tRPC mount
│       └── services/
│           └── gemini-scanner.ts    # Gemini API final scan
│
├── packages/
│   ├── api/                  # tRPC routers
│   │   ├── package.json
│   │   └── src/
│   │       ├── index.ts      # Root router + Hono adapter
│   │       ├── context.ts    # tRPC context (db, auth session)
│   │       ├── services/
│   │       │   ├── guardian-engine.ts    # Rule matching orchestrator
│   │       │   ├── rule-matcher.ts      # Keyword matching logic
│   │       │   └── excel-exporter.ts    # Excel export
│   │       └── routers/
│   │           ├── index.ts
│   │           ├── project.ts
│   │           ├── quotation.ts
│   │           ├── item.ts
│   │           ├── alert.ts
│   │           └── guardian.ts   # check-item, cross-trade-check, final-scan
│   │
│   ├── auth/                 # Better-Auth config
│   │   ├── package.json
│   │   └── src/
│   │       └── index.ts
│   │
│   ├── db/                   # Drizzle ORM + schema
│   │   ├── package.json
│   │   ├── drizzle.config.ts
│   │   └── src/
│   │       ├── index.ts      # Drizzle client (Neon)
│   │       ├── schema/
│   │       │   ├── index.ts
│   │       │   ├── auth.ts
│   │       │   ├── project.ts
│   │       │   ├── quotation.ts
│   │       │   ├── alert.ts
│   │       │   └── rule.ts
│   │       └── seed/
│   │           ├── index.ts       # Seed runner
│   │           └── rules.ts      # MVP rules from PRIOR_KNOWLEDGE.md
│   │
│   └── shared/               # Shared types + constants
│       ├── package.json
│       └── src/
│           ├── index.ts
│           ├── trades.ts     # Trade codes, display names, sort order
│           └── types.ts      # Shared enums + types
```

---

## Task 1: Scaffold Better-T Stack Monorepo

**Files:**
- Create: `nooko-quotation-guardian/` (entire scaffolded project)
- Modify: `.gitignore` (add `nooko-quotation-guardian/node_modules`)

- [ ] **Step 1: Scaffold project with Better-T Stack CLI**

```bash
cd /Users/stephenkao/Nooko_Your_InteriorDeco_Ai
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

If the CLI prompts interactively instead of accepting flags, answer:
- Runtime: bun
- Frontend: tanstack-router
- Backend: hono
- API: trpc
- Database: postgres
- ORM: drizzle
- Auth: better-auth
- Addons: turborepo, biome
- DB setup: neon

- [ ] **Step 2: Install additional dependencies**

```bash
cd /Users/stephenkao/Nooko_Your_InteriorDeco_Ai/nooko-quotation-guardian

# Frontend deps
cd apps/web
bun add @tanstack/react-table react-hook-form @hookform/resolvers
cd ../..

# Server deps
cd server
bun add @google/genai xlsx
cd ..

# shadcn/ui setup (in apps/web)
cd apps/web
bunx shadcn@latest init -y
bunx shadcn@latest add button card input label select badge dialog form textarea progress separator scroll-area
cd ../..
```

- [ ] **Step 3: Verify scaffold works**

```bash
cd /Users/stephenkao/Nooko_Your_InteriorDeco_Ai/nooko-quotation-guardian
bun install
bun run build
```

Expected: Build completes without errors.

- [ ] **Step 4: Create .env.example**

Create `/Users/stephenkao/Nooko_Your_InteriorDeco_Ai/nooko-quotation-guardian/.env.example`:

```
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
BETTER_AUTH_SECRET=your-secret-here
GEMINI_API_KEY=your-gemini-api-key
```

- [ ] **Step 5: Commit**

```bash
git add nooko-quotation-guardian/
git commit -m "feat: scaffold quotation guardian monorepo (Better-T Stack)"
```

---

## Task 2: Shared Package — Trade Constants & Types

**Files:**
- Create: `nooko-quotation-guardian/packages/shared/package.json`
- Create: `nooko-quotation-guardian/packages/shared/src/index.ts`
- Create: `nooko-quotation-guardian/packages/shared/src/trades.ts`
- Create: `nooko-quotation-guardian/packages/shared/src/types.ts`
- Create: `nooko-quotation-guardian/packages/shared/tsconfig.json`

- [ ] **Step 1: Create shared package.json**

```json
{
  "name": "@repo/shared",
  "version": "0.0.1",
  "private": true,
  "type": "module",
  "exports": { ".": "./src/index.ts" },
  "scripts": { "typecheck": "tsc --noEmit" }
}
```

- [ ] **Step 2: Create trades.ts**

```typescript
// nooko-quotation-guardian/packages/shared/src/trades.ts

export const TRADE_CODES = [
  "protection",
  "demolition",
  "masonry",
  "waterproof",
  "plumbing_electrical",
  "carpentry",
  "painting",
  "wallpaper",
  "flooring",
  "cabinet_kitchen",
  "hvac",
  "door_window",
  "cleaning",
] as const;

export type TradeCode = (typeof TRADE_CODES)[number];

export const TRADE_DISPLAY_NAMES: Record<TradeCode, string> = {
  protection: "保護工程",
  demolition: "拆除工程",
  masonry: "泥作工程",
  waterproof: "防水工程",
  plumbing_electrical: "水電工程",
  carpentry: "木作工程",
  painting: "油漆工程",
  wallpaper: "壁紙工程",
  flooring: "地板工程",
  cabinet_kitchen: "系統櫃/廚具",
  hvac: "空調工程",
  door_window: "門窗工程",
  cleaning: "清潔工程",
};

export const TRADE_SORT_ORDER: Record<TradeCode, number> = Object.fromEntries(
  TRADE_CODES.map((code, i) => [code, i + 1])
) as Record<TradeCode, number>;
```

- [ ] **Step 3: Create types.ts**

```typescript
// nooko-quotation-guardian/packages/shared/src/types.ts

export const PROJECT_TYPES = ["residential", "commercial"] as const;
export type ProjectType = (typeof PROJECT_TYPES)[number];

export const AGE_TIERS = [0, 5, 10, 20, 30] as const;
export type AgeTier = (typeof AGE_TIERS)[number];

export const AGE_TIER_LABELS: Record<number, string> = {
  0: "0-5 年（新成屋）",
  5: "5-10 年",
  10: "10-20 年（中古屋）",
  20: "20-30 年",
  30: "30 年以上（老屋）",
};

export const SECTION_STATUSES = ["pending", "editing", "completed"] as const;
export type SectionStatus = (typeof SECTION_STATUSES)[number];

export const ALERT_SEVERITIES = ["red", "yellow"] as const;
export type AlertSeverity = (typeof ALERT_SEVERITIES)[number];

export const ALERT_STATUSES = ["pending", "accepted", "ignored"] as const;
export type AlertStatus = (typeof ALERT_STATUSES)[number];

export const ALERT_SOURCES = ["rule", "gemini"] as const;
export type AlertSource = (typeof ALERT_SOURCES)[number];

export const ITEM_SOURCES = ["manual", "auto_added"] as const;
export type ItemSource = (typeof ITEM_SOURCES)[number];

export const RULE_TYPES = [
  "dependency",
  "linked",
  "condition",
  "conflict",
  "quantity",
] as const;
export type RuleType = (typeof RULE_TYPES)[number];

export const RULE_SCOPES = ["residential", "commercial", "shared"] as const;
export type RuleScope = (typeof RULE_SCOPES)[number];
```

- [ ] **Step 4: Create index.ts barrel export**

```typescript
// nooko-quotation-guardian/packages/shared/src/index.ts
export * from "./trades";
export * from "./types";
```

- [ ] **Step 5: Add shared package to workspace references**

Add `"@repo/shared": "workspace:*"` to the dependencies of `packages/db/package.json`, `packages/api/package.json`, `server/package.json`, and `apps/web/package.json`.

Then run:
```bash
cd /Users/stephenkao/Nooko_Your_InteriorDeco_Ai/nooko-quotation-guardian
bun install
```

- [ ] **Step 6: Commit**

```bash
git add nooko-quotation-guardian/packages/shared/
git commit -m "feat: add shared package with trade constants and types"
```

---

## Task 3: Database Schema (Drizzle ORM)

**Files:**
- Create: `nooko-quotation-guardian/packages/db/src/schema/project.ts`
- Create: `nooko-quotation-guardian/packages/db/src/schema/quotation.ts`
- Create: `nooko-quotation-guardian/packages/db/src/schema/alert.ts`
- Create: `nooko-quotation-guardian/packages/db/src/schema/rule.ts`
- Modify: `nooko-quotation-guardian/packages/db/src/schema/index.ts`

- [ ] **Step 1: Create project schema**

```typescript
// nooko-quotation-guardian/packages/db/src/schema/project.ts
import {
  pgTable,
  text,
  integer,
  boolean,
  timestamp,
  pgEnum,
} from "drizzle-orm/pg-core";
import { createId } from "@paralleldrive/cuid2";
import { user } from "./auth";

export const projectTypeEnum = pgEnum("project_type", [
  "residential",
  "commercial",
]);

export const projectStatusEnum = pgEnum("project_status", [
  "draft",
  "in_progress",
  "completed",
]);

export const project = pgTable("project", {
  id: text("id")
    .primaryKey()
    .$defaultFn(() => createId()),
  userId: text("user_id")
    .notNull()
    .references(() => user.id),
  name: text("name").notNull(),
  type: projectTypeEnum("type").notNull(),
  ageTier: integer("age_tier"), // nullable for commercial
  area: integer("area").notNull(), // 坪數
  floor: integer("floor").notNull(),
  hasElevator: boolean("has_elevator").notNull().default(false),
  status: projectStatusEnum("status").notNull().default("draft"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at")
    .notNull()
    .defaultNow()
    .$onUpdate(() => new Date()),
});
```

- [ ] **Step 2: Create quotation schema**

```typescript
// nooko-quotation-guardian/packages/db/src/schema/quotation.ts
import {
  pgTable,
  text,
  integer,
  timestamp,
  pgEnum,
  real,
} from "drizzle-orm/pg-core";
import { createId } from "@paralleldrive/cuid2";
import { project } from "./project";

export const sectionStatusEnum = pgEnum("section_status", [
  "pending",
  "editing",
  "completed",
]);

export const itemSourceEnum = pgEnum("item_source", [
  "manual",
  "auto_added",
]);

export const quotation = pgTable("quotation", {
  id: text("id")
    .primaryKey()
    .$defaultFn(() => createId()),
  projectId: text("project_id")
    .notNull()
    .unique()
    .references(() => project.id, { onDelete: "cascade" }),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at")
    .notNull()
    .defaultNow()
    .$onUpdate(() => new Date()),
  exportedAt: timestamp("exported_at"),
});

export const quotationSection = pgTable("quotation_section", {
  id: text("id")
    .primaryKey()
    .$defaultFn(() => createId()),
  quotationId: text("quotation_id")
    .notNull()
    .references(() => quotation.id, { onDelete: "cascade" }),
  tradeCode: text("trade_code").notNull(),
  sortOrder: integer("sort_order").notNull(),
  status: sectionStatusEnum("status").notNull().default("pending"),
});

export const quotationItem = pgTable("quotation_item", {
  id: text("id")
    .primaryKey()
    .$defaultFn(() => createId()),
  sectionId: text("section_id")
    .notNull()
    .references(() => quotationSection.id, { onDelete: "cascade" }),
  name: text("name").notNull(),
  unit: text("unit").notNull(),
  quantity: real("quantity").notNull(),
  source: itemSourceEnum("source").notNull().default("manual"),
  addedFromAlertId: text("added_from_alert_id"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});
```

- [ ] **Step 3: Create alert schema**

```typescript
// nooko-quotation-guardian/packages/db/src/schema/alert.ts
import {
  pgTable,
  text,
  timestamp,
  pgEnum,
  real,
} from "drizzle-orm/pg-core";
import { createId } from "@paralleldrive/cuid2";
import { quotation, quotationSection, quotationItem } from "./quotation";
import { rule } from "./rule";

export const alertSeverityEnum = pgEnum("alert_severity", ["red", "yellow"]);
export const alertStatusEnum = pgEnum("alert_status", [
  "pending",
  "accepted",
  "ignored",
]);
export const alertSourceEnum = pgEnum("alert_source", ["rule", "gemini"]);

export const alert = pgTable("alert", {
  id: text("id")
    .primaryKey()
    .$defaultFn(() => createId()),
  quotationId: text("quotation_id")
    .notNull()
    .references(() => quotation.id, { onDelete: "cascade" }),
  sectionId: text("section_id")
    .notNull()
    .references(() => quotationSection.id, { onDelete: "cascade" }),
  source: alertSourceEnum("source").notNull().default("rule"),
  ruleId: text("rule_id").references(() => rule.id),
  triggerItemId: text("trigger_item_id").references(() => quotationItem.id),
  severity: alertSeverityEnum("severity").notNull(),
  message: text("message").notNull(),
  suggestion: text("suggestion"),
  status: alertStatusEnum("status").notNull().default("pending"),
  ignoreReason: text("ignore_reason"),
  aiConfidence: real("ai_confidence"),
  aiReasoning: text("ai_reasoning"),
  resolvedAt: timestamp("resolved_at"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});
```

- [ ] **Step 4: Create rule schema**

```typescript
// nooko-quotation-guardian/packages/db/src/schema/rule.ts
import {
  pgTable,
  text,
  integer,
  boolean,
  pgEnum,
  jsonb,
} from "drizzle-orm/pg-core";
import { createId } from "@paralleldrive/cuid2";

export const ruleTypeEnum = pgEnum("rule_type", [
  "dependency",
  "linked",
  "condition",
  "conflict",
  "quantity",
]);

export const ruleSeverityEnum = pgEnum("rule_severity", ["red", "yellow"]);

export const ruleScopeEnum = pgEnum("rule_scope", [
  "residential",
  "commercial",
  "shared",
]);

export const rule = pgTable("rule", {
  id: text("id")
    .primaryKey()
    .$defaultFn(() => createId()),
  type: ruleTypeEnum("type").notNull(),
  triggerTrade: text("trigger_trade").notNull(),
  triggerItemPattern: jsonb("trigger_item_pattern").$type<string[]>(),
  conditionJson: jsonb("condition_json").$type<Record<string, unknown>>(),
  actionTrade: text("action_trade"),
  actionItem: text("action_item"),
  messageTemplate: text("message_template").notNull(),
  severity: ruleSeverityEnum("severity").notNull(),
  scope: ruleScopeEnum("scope").notNull().default("shared"),
  ageTierMin: integer("age_tier_min"),
  ageTierMax: integer("age_tier_max"),
  active: boolean("active").notNull().default(true),
});
```

- [ ] **Step 5: Update schema barrel export**

```typescript
// nooko-quotation-guardian/packages/db/src/schema/index.ts
export * from "./auth";
export * from "./project";
export * from "./quotation";
export * from "./alert";
export * from "./rule";
```

- [ ] **Step 6: Install cuid2, then generate and run migration**

```bash
cd /Users/stephenkao/Nooko_Your_InteriorDeco_Ai/nooko-quotation-guardian
cd packages/db
bun add @paralleldrive/cuid2
bun run db:generate
bun run db:migrate
```

Expected: Migration files created in `packages/db/drizzle/` and applied to the database.

- [ ] **Step 7: Verify with typecheck**

```bash
cd /Users/stephenkao/Nooko_Your_InteriorDeco_Ai/nooko-quotation-guardian
bun run typecheck
```

Expected: No type errors.

- [ ] **Step 8: Commit**

```bash
git add nooko-quotation-guardian/packages/db/
git commit -m "feat: add database schema for project, quotation, alert, rule"
```

---

## Task 4: Seed Rules from PRIOR_KNOWLEDGE.md

**Files:**
- Create: `nooko-quotation-guardian/packages/db/src/seed/rules.ts`
- Create: `nooko-quotation-guardian/packages/db/src/seed/index.ts`
- Modify: `nooko-quotation-guardian/packages/db/package.json` (add seed script)

- [ ] **Step 1: Create seed rules**

Create `nooko-quotation-guardian/packages/db/src/seed/rules.ts` with the MVP rules extracted from `specs/003-quotation-guardian/PRIOR_KNOWLEDGE.md`. Include at minimum these critical rules:

```typescript
// nooko-quotation-guardian/packages/db/src/seed/rules.ts
import type { InferInsertModel } from "drizzle-orm";
import { rule } from "../schema/rule";

type NewRule = Omit<InferInsertModel<typeof rule>, "id">;

export const seedRules: NewRule[] = [
  // ========== 拆除工程 ==========
  {
    type: "dependency",
    triggerTrade: "demolition",
    triggerItemPattern: ["拆除", "打除", "打石", "拆牆"],
    conditionJson: { requires: { trade: "demolition", item_keywords: ["垃圾清運"] } },
    actionTrade: "demolition",
    actionItem: "垃圾清運",
    messageTemplate: "有拆除工程但缺少「垃圾清運」，這是最常被漏報的項目",
    severity: "red",
    scope: "shared",
    ageTierMin: null,
    ageTierMax: null,
    active: true,
  },
  {
    type: "dependency",
    triggerTrade: "demolition",
    triggerItemPattern: ["地磚拆除", "打見底"],
    conditionJson: { requires: { trade: "masonry", item_keywords: ["整平", "粉光"] } },
    actionTrade: "masonry",
    actionItem: "地面整平",
    messageTemplate: "地磚拆除（打見底）後需要地面整平",
    severity: "red",
    scope: "shared",
    ageTierMin: null,
    ageTierMax: null,
    active: true,
  },
  {
    type: "dependency",
    triggerTrade: "demolition",
    triggerItemPattern: ["地磚拆除", "打見底"],
    conditionJson: { requires: { trade: "waterproof", item_keywords: ["防水"] } },
    actionTrade: "waterproof",
    actionItem: "防水施作",
    messageTemplate: "地磚拆除（打見底）後需要重做防水",
    severity: "red",
    scope: "shared",
    ageTierMin: null,
    ageTierMax: null,
    active: true,
  },
  {
    type: "dependency",
    triggerTrade: "demolition",
    triggerItemPattern: ["衛浴設備拆除"],
    conditionJson: { requires: { trade: "plumbing_electrical", item_keywords: ["封管"] } },
    actionTrade: "plumbing_electrical",
    actionItem: "封管",
    messageTemplate: "衛浴設備拆除後需要封管處理",
    severity: "red",
    scope: "shared",
    ageTierMin: null,
    ageTierMax: null,
    active: true,
  },
  {
    type: "dependency",
    triggerTrade: "demolition",
    triggerItemPattern: ["廚具拆除"],
    conditionJson: { requires: { trade: "plumbing_electrical", item_keywords: ["瓦斯管封閉", "瓦斯"] } },
    actionTrade: "plumbing_electrical",
    actionItem: "瓦斯管封閉",
    messageTemplate: "廚具拆除後需要瓦斯管封閉",
    severity: "red",
    scope: "shared",
    ageTierMin: null,
    ageTierMax: null,
    active: true,
  },

  // ========== 保護工程 ==========
  {
    type: "condition",
    triggerTrade: "protection",
    triggerItemPattern: null,
    conditionJson: { site: { has_elevator: true } },
    actionTrade: "protection",
    actionItem: "電梯保護",
    messageTemplate: "大樓案場建議加入電梯保護",
    severity: "yellow",
    scope: "shared",
    ageTierMin: null,
    ageTierMax: null,
    active: true,
  },
  {
    type: "condition",
    triggerTrade: "protection",
    triggerItemPattern: null,
    conditionJson: { site: { has_elevator: true } },
    actionTrade: "protection",
    actionItem: "公共區域保護",
    messageTemplate: "大樓案場建議加入公共區域保護（含牆面）",
    severity: "yellow",
    scope: "shared",
    ageTierMin: null,
    ageTierMax: null,
    active: true,
  },

  // ========== 防水工程 ==========
  {
    type: "linked",
    triggerTrade: "waterproof",
    triggerItemPattern: ["防水施作", "防水塗佈", "防水"],
    conditionJson: { requires: { trade: "waterproof", item_keywords: ["試水", "試水測試"] } },
    actionTrade: "waterproof",
    actionItem: "試水測試（至少24hr）",
    messageTemplate: "有防水施作必須搭配試水測試（至少 24 小時）",
    severity: "red",
    scope: "shared",
    ageTierMin: null,
    ageTierMax: null,
    active: true,
  },

  // ========== 水電工程（屋齡相關）==========
  {
    type: "condition",
    triggerTrade: "plumbing_electrical",
    triggerItemPattern: null,
    conditionJson: { site: { age_tier_min: 20 } },
    actionTrade: "plumbing_electrical",
    actionItem: "全室電線更換",
    messageTemplate: "屋齡 20 年以上建議全室電線更換（電線壽命約 9 年）",
    severity: "yellow",
    scope: "residential",
    ageTierMin: 20,
    ageTierMax: null,
    active: true,
  },
  {
    type: "condition",
    triggerTrade: "plumbing_electrical",
    triggerItemPattern: null,
    conditionJson: { site: { age_tier_min: 20 } },
    actionTrade: "plumbing_electrical",
    actionItem: "給水管更新（含壓力測試）",
    messageTemplate: "屋齡 20 年以上建議更新給水管並做壓力測試",
    severity: "yellow",
    scope: "residential",
    ageTierMin: 20,
    ageTierMax: null,
    active: true,
  },

  // ========== 泥作工程 ==========
  {
    type: "dependency",
    triggerTrade: "masonry",
    triggerItemPattern: ["貼磚", "鋪磚", "地壁磚", "壁磚", "地磚"],
    conditionJson: { requires: { trade: "masonry", item_keywords: ["門檻石"] } },
    actionTrade: "masonry",
    actionItem: "門檻石安裝",
    messageTemplate: "有磁磚鋪設建議確認是否需要門檻石（浴室+廚房）",
    severity: "yellow",
    scope: "shared",
    ageTierMin: null,
    ageTierMax: null,
    active: true,
  },

  // ========== 數量規則 ==========
  {
    type: "quantity",
    triggerTrade: "demolition",
    triggerItemPattern: ["垃圾清運"],
    conditionJson: { quantity_ratio: { per_area: 10, expected: 2, unit: "車" } },
    actionTrade: null,
    actionItem: null,
    messageTemplate: "垃圾清運數量參考：每 10 坪約 2 車，請確認數量是否合理",
    severity: "yellow",
    scope: "shared",
    ageTierMin: null,
    ageTierMax: null,
    active: true,
  },

  // ========== 清潔工程 ==========
  {
    type: "dependency",
    triggerTrade: "cleaning",
    triggerItemPattern: ["粗清", "細清", "清潔"],
    conditionJson: null,
    actionTrade: null,
    actionItem: null,
    messageTemplate: "清潔工程建議包含粗清及細清兩階段",
    severity: "yellow",
    scope: "shared",
    ageTierMin: null,
    ageTierMax: null,
    active: true,
  },
];
```

**Note to implementor:** This is a starter set. Add more rules by reading `specs/003-quotation-guardian/PRIOR_KNOWLEDGE.md` — every "常見漏項" entry should become a rule. Target 30-50 rules for MVP.

- [ ] **Step 2: Create seed runner**

```typescript
// nooko-quotation-guardian/packages/db/src/seed/index.ts
import { db } from "../index";
import { rule } from "../schema/rule";
import { seedRules } from "./rules";

async function seed() {
  console.log("Clearing existing rules...");
  await db.delete(rule);
  console.log("Seeding rules...");
  await db.insert(rule).values(seedRules);
  console.log(`Seeded ${seedRules.length} rules.`);
  process.exit(0);
}

seed().catch((e) => {
  console.error("Seed failed:", e);
  process.exit(1);
});
```

- [ ] **Step 3: Add seed script to package.json**

Add to `packages/db/package.json` scripts:
```json
"db:seed": "bun run src/seed/index.ts"
```

- [ ] **Step 4: Run seed**

```bash
cd /Users/stephenkao/Nooko_Your_InteriorDeco_Ai/nooko-quotation-guardian/packages/db
bun run db:seed
```

Expected: "Seeded N rules."

- [ ] **Step 5: Commit**

```bash
git add nooko-quotation-guardian/packages/db/src/seed/
git commit -m "feat: add seed rules from PRIOR_KNOWLEDGE.md"
```

---

## Task 5: tRPC Routers — Project & Quotation CRUD

**Files:**
- Create: `nooko-quotation-guardian/packages/api/src/routers/project.ts`
- Create: `nooko-quotation-guardian/packages/api/src/routers/quotation.ts`
- Create: `nooko-quotation-guardian/packages/api/src/routers/item.ts`
- Create: `nooko-quotation-guardian/packages/api/src/routers/alert.ts`
- Modify: `nooko-quotation-guardian/packages/api/src/routers/index.ts`

- [ ] **Step 1: Create project router**

```typescript
// nooko-quotation-guardian/packages/api/src/routers/project.ts
import { z } from "zod";
import { router, protectedProcedure } from "../trpc"; // adjust import to match scaffold
import { project } from "@repo/db/schema";
import { quotation, quotationSection } from "@repo/db/schema";
import { eq } from "drizzle-orm";
import { TRADE_CODES, TRADE_SORT_ORDER } from "@repo/shared";

export const projectRouter = router({
  create: protectedProcedure
    .input(
      z.object({
        name: z.string().min(1),
        type: z.enum(["residential", "commercial"]),
        ageTier: z.number().nullable(),
        area: z.number().int().positive(),
        floor: z.number().int().positive(),
        hasElevator: z.boolean(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const [newProject] = await ctx.db
        .insert(project)
        .values({ ...input, userId: ctx.session.user.id })
        .returning();

      // Auto-create quotation + 13 sections
      const [newQuotation] = await ctx.db
        .insert(quotation)
        .values({ projectId: newProject.id })
        .returning();

      await ctx.db.insert(quotationSection).values(
        TRADE_CODES.map((code) => ({
          quotationId: newQuotation.id,
          tradeCode: code,
          sortOrder: TRADE_SORT_ORDER[code],
        }))
      );

      return newProject;
    }),

  list: protectedProcedure.query(async ({ ctx }) => {
    return ctx.db
      .select()
      .from(project)
      .where(eq(project.userId, ctx.session.user.id))
      .orderBy(project.createdAt);
  }),

  get: protectedProcedure
    .input(z.object({ id: z.string() }))
    .query(async ({ ctx, input }) => {
      const [p] = await ctx.db
        .select()
        .from(project)
        .where(eq(project.id, input.id));
      return p ?? null;
    }),
});
```

- [ ] **Step 2: Create quotation router**

```typescript
// nooko-quotation-guardian/packages/api/src/routers/quotation.ts
import { z } from "zod";
import { router, protectedProcedure } from "../trpc";
import { quotation, quotationSection } from "@repo/db/schema";
import { eq } from "drizzle-orm";

export const quotationRouter = router({
  getByProject: protectedProcedure
    .input(z.object({ projectId: z.string() }))
    .query(async ({ ctx, input }) => {
      const [q] = await ctx.db
        .select()
        .from(quotation)
        .where(eq(quotation.projectId, input.projectId));
      return q ?? null;
    }),

  getSections: protectedProcedure
    .input(z.object({ quotationId: z.string() }))
    .query(async ({ ctx, input }) => {
      return ctx.db
        .select()
        .from(quotationSection)
        .where(eq(quotationSection.quotationId, input.quotationId))
        .orderBy(quotationSection.sortOrder);
    }),

  updateSectionStatus: protectedProcedure
    .input(
      z.object({
        sectionId: z.string(),
        status: z.enum(["pending", "editing", "completed"]),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const [updated] = await ctx.db
        .update(quotationSection)
        .set({ status: input.status })
        .where(eq(quotationSection.id, input.sectionId))
        .returning();
      return updated;
    }),
});
```

- [ ] **Step 3: Create item router**

```typescript
// nooko-quotation-guardian/packages/api/src/routers/item.ts
import { z } from "zod";
import { router, protectedProcedure } from "../trpc";
import { quotationItem } from "@repo/db/schema";
import { alert } from "@repo/db/schema";
import { eq, and } from "drizzle-orm";

export const itemRouter = router({
  list: protectedProcedure
    .input(z.object({ sectionId: z.string() }))
    .query(async ({ ctx, input }) => {
      return ctx.db
        .select()
        .from(quotationItem)
        .where(eq(quotationItem.sectionId, input.sectionId))
        .orderBy(quotationItem.createdAt);
    }),

  create: protectedProcedure
    .input(
      z.object({
        sectionId: z.string(),
        name: z.string().min(1),
        unit: z.string().min(1),
        quantity: z.number().positive(),
        source: z.enum(["manual", "auto_added"]).default("manual"),
        addedFromAlertId: z.string().nullable().default(null),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const [item] = await ctx.db
        .insert(quotationItem)
        .values(input)
        .returning();
      return item;
    }),

  update: protectedProcedure
    .input(
      z.object({
        id: z.string(),
        name: z.string().min(1),
        unit: z.string().min(1),
        quantity: z.number().positive(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const { id, ...data } = input;
      const [updated] = await ctx.db
        .update(quotationItem)
        .set(data)
        .where(eq(quotationItem.id, id))
        .returning();
      return updated;
    }),

  delete: protectedProcedure
    .input(z.object({ id: z.string() }))
    .mutation(async ({ ctx, input }) => {
      // Edge case: if item triggered alerts, mark them accepted
      await ctx.db
        .update(alert)
        .set({ status: "accepted", resolvedAt: new Date() })
        .where(
          and(
            eq(alert.triggerItemId, input.id),
            eq(alert.status, "pending")
          )
        );

      // Edge case: if item was auto-added from alert, reopen that alert
      const [deletedItem] = await ctx.db
        .select()
        .from(quotationItem)
        .where(eq(quotationItem.id, input.id));

      if (deletedItem?.addedFromAlertId) {
        await ctx.db
          .update(alert)
          .set({ status: "pending", resolvedAt: null })
          .where(eq(alert.id, deletedItem.addedFromAlertId));
      }

      await ctx.db
        .delete(quotationItem)
        .where(eq(quotationItem.id, input.id));
      return { success: true };
    }),
});
```

- [ ] **Step 4: Create alert router**

```typescript
// nooko-quotation-guardian/packages/api/src/routers/alert.ts
import { z } from "zod";
import { router, protectedProcedure } from "../trpc";
import { alert } from "@repo/db/schema";
import { quotationItem } from "@repo/db/schema";
import { eq, and } from "drizzle-orm";

export const alertRouter = router({
  listBySection: protectedProcedure
    .input(z.object({ sectionId: z.string() }))
    .query(async ({ ctx, input }) => {
      return ctx.db
        .select()
        .from(alert)
        .where(eq(alert.sectionId, input.sectionId))
        .orderBy(alert.createdAt);
    }),

  listByQuotation: protectedProcedure
    .input(z.object({ quotationId: z.string() }))
    .query(async ({ ctx, input }) => {
      return ctx.db
        .select()
        .from(alert)
        .where(eq(alert.quotationId, input.quotationId))
        .orderBy(alert.createdAt);
    }),

  accept: protectedProcedure
    .input(
      z.object({
        alertId: z.string(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      // Get the alert with its rule info
      const [a] = await ctx.db
        .select()
        .from(alert)
        .where(eq(alert.id, input.alertId));

      if (!a) throw new Error("Alert not found");

      // Auto-add the suggested item to the alert's target section
      let addedItemId: string | null = null;
      if (a.suggestion) {
        const [newItem] = await ctx.db
          .insert(quotationItem)
          .values({
            sectionId: a.sectionId, // Use alert's own sectionId (target section)
            name: a.suggestion,
            unit: "式",
            quantity: 1,
            source: "auto_added",
            addedFromAlertId: a.id,
          })
          .returning();
        addedItemId = newItem.id;
      }

      // Mark alert as accepted
      const [updated] = await ctx.db
        .update(alert)
        .set({ status: "accepted", resolvedAt: new Date() })
        .where(eq(alert.id, input.alertId))
        .returning();

      return { alert: updated, addedItemId };
    }),

  ignore: protectedProcedure
    .input(
      z.object({
        alertId: z.string(),
        reason: z.string().min(1),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const [updated] = await ctx.db
        .update(alert)
        .set({
          status: "ignored",
          ignoreReason: input.reason,
          resolvedAt: new Date(),
        })
        .where(eq(alert.id, input.alertId))
        .returning();
      return updated;
    }),
});
```

- [ ] **Step 5: Wire routers into root**

Update `packages/api/src/routers/index.ts`:

```typescript
import { router } from "../trpc";
import { projectRouter } from "./project";
import { quotationRouter } from "./quotation";
import { itemRouter } from "./item";
import { alertRouter } from "./alert";

export const appRouter = router({
  project: projectRouter,
  quotation: quotationRouter,
  item: itemRouter,
  alert: alertRouter,
});

export type AppRouter = typeof appRouter;
```

- [ ] **Step 6: Verify typecheck**

```bash
cd /Users/stephenkao/Nooko_Your_InteriorDeco_Ai/nooko-quotation-guardian
bun run typecheck
```

- [ ] **Step 7: Commit**

```bash
git add nooko-quotation-guardian/packages/api/
git commit -m "feat: add tRPC routers for project, quotation, item, alert"
```

---

## Task 6: Guardian Engine — Rule Matcher

**Files:**
- Create: `nooko-quotation-guardian/packages/api/src/services/rule-matcher.ts`
- Create: `nooko-quotation-guardian/packages/api/src/services/guardian-engine.ts`
- Create: `nooko-quotation-guardian/packages/api/src/routers/guardian.ts`
- Modify: `nooko-quotation-guardian/packages/api/src/routers/index.ts`

- [ ] **Step 1: Create rule-matcher.ts**

```typescript
// nooko-quotation-guardian/packages/api/src/services/rule-matcher.ts
import { db } from "@repo/db";
import { rule } from "@repo/db/schema";
import { eq, and, or, isNull, lte, gt } from "drizzle-orm";
import type { RuleType } from "@repo/shared";

interface MatchContext {
  projectType: "residential" | "commercial";
  ageTier: number | null;
  hasElevator: boolean;
  area: number;
}

interface ItemInput {
  name: string;
  unit: string;
  quantity: number;
  tradeCode: string;
}

interface AllItems {
  [tradeCode: string]: ItemInput[];
}

export interface MatchedRule {
  ruleId: string;
  type: RuleType;
  message: string;
  suggestion: string | null;
  severity: "red" | "yellow";
  actionTrade: string | null;
  actionItem: string | null;
}

/**
 * Check a single item against all applicable rules.
 */
export async function matchItemRules(
  item: ItemInput,
  context: MatchContext,
  allItems: AllItems
): Promise<MatchedRule[]> {
  // Load applicable rules for this trade
  const scopeFilter =
    context.projectType === "residential"
      ? or(eq(rule.scope, "residential"), eq(rule.scope, "shared"))
      : or(eq(rule.scope, "commercial"), eq(rule.scope, "shared"));

  const rules = await db
    .select()
    .from(rule)
    .where(
      and(
        eq(rule.triggerTrade, item.tradeCode),
        eq(rule.active, true),
        scopeFilter
      )
    );

  const matched: MatchedRule[] = [];

  for (const r of rules) {
    // Check age tier applicability
    if (r.ageTierMin !== null && (context.ageTier === null || context.ageTier < r.ageTierMin)) continue;
    if (r.ageTierMax !== null && (context.ageTier === null || context.ageTier >= r.ageTierMax)) continue;

    // Check trigger pattern match
    const patterns = r.triggerItemPattern as string[] | null;
    if (patterns && patterns.length > 0) {
      const hit = patterns.some((p) => item.name.includes(p));
      if (!hit) continue;
    }

    const condition = r.conditionJson as Record<string, unknown> | null;

    // --- Handle each rule type ---

    if (r.type === "dependency" || r.type === "linked") {
      // Check if the required item already exists
      if (condition?.requires) {
        const req = condition.requires as { trade: string; item_keywords: string[] };
        const targetItems = allItems[req.trade] || [];
        const alreadyHas = targetItems.some((existing) =>
          req.item_keywords.some((kw) => existing.name.includes(kw))
        );
        if (alreadyHas) continue; // requirement already satisfied
      }
    } else if (r.type === "condition") {
      // Site-condition rules (e.g., elevator protection, old house rewiring)
      // These should only be evaluated once per section entry, not per item.
      // The caller (checkSectionConditions) handles this — skip here.
      continue;
    } else if (r.type === "conflict") {
      // Check if conflicting item exists
      if (condition?.conflicts_with) {
        const cw = condition.conflicts_with as { item_keywords: string[] };
        const allTradeItems = Object.values(allItems).flat();
        const hasConflict = allTradeItems.some((existing) =>
          cw.item_keywords.some((kw) => existing.name.includes(kw))
        );
        if (!hasConflict) continue; // no conflict found
      }
    } else if (r.type === "quantity") {
      // Check quantity reasonableness against area
      if (condition?.quantity_ratio) {
        const qr = condition.quantity_ratio as { per_area: number; expected: number; unit: string };
        const expectedQty = (context.area / qr.per_area) * qr.expected;
        const ratio = item.quantity / expectedQty;
        if (ratio >= 0.5 && ratio <= 2.0) continue; // within reasonable range
      }
    }

    matched.push({
      ruleId: r.id,
      type: r.type as RuleType,
      message: r.messageTemplate,
      suggestion: r.actionItem,
      severity: r.severity as "red" | "yellow",
      actionTrade: r.actionTrade,
      actionItem: r.actionItem,
    });
  }

  return matched;
}

/**
 * Check condition-type rules for a section (called once on section entry).
 */
export async function checkSectionConditions(
  tradeCode: string,
  context: MatchContext,
  allItems: AllItems
): Promise<MatchedRule[]> {
  const scopeFilter =
    context.projectType === "residential"
      ? or(eq(rule.scope, "residential"), eq(rule.scope, "shared"))
      : or(eq(rule.scope, "commercial"), eq(rule.scope, "shared"));

  const rules = await db
    .select()
    .from(rule)
    .where(
      and(
        eq(rule.triggerTrade, tradeCode),
        eq(rule.type, "condition"),
        eq(rule.active, true),
        scopeFilter
      )
    );

  const matched: MatchedRule[] = [];

  for (const r of rules) {
    if (r.ageTierMin !== null && (context.ageTier === null || context.ageTier < r.ageTierMin)) continue;
    if (r.ageTierMax !== null && (context.ageTier === null || context.ageTier >= r.ageTierMax)) continue;

    const condition = r.conditionJson as Record<string, unknown> | null;
    if (condition?.site) {
      const site = condition.site as Record<string, unknown>;
      if (site.has_elevator !== undefined && site.has_elevator !== context.hasElevator) continue;
      if (site.age_tier_min !== undefined && (context.ageTier === null || context.ageTier < (site.age_tier_min as number))) continue;
    }

    // Check if suggested item already exists
    if (r.actionTrade && r.actionItem) {
      const targetItems = allItems[r.actionTrade] || [];
      const alreadyHas = targetItems.some((existing) => existing.name.includes(r.actionItem!));
      if (alreadyHas) continue;
    }

    matched.push({
      ruleId: r.id,
      type: r.type as RuleType,
      message: r.messageTemplate,
      suggestion: r.actionItem,
      severity: r.severity as "red" | "yellow",
      actionTrade: r.actionTrade,
      actionItem: r.actionItem,
    });
  }

  return matched;
}
```

- [ ] **Step 2: Create guardian-engine.ts**

```typescript
// nooko-quotation-guardian/packages/api/src/services/guardian-engine.ts
import { db } from "@repo/db";
import {
  quotationItem,
  quotationSection,
  alert,
  project,
  quotation,
  rule,
} from "@repo/db/schema";
import { eq, and, or, inArray } from "drizzle-orm";
import { matchItemRules, checkSectionConditions, type MatchedRule } from "./rule-matcher";
import type { TRADE_CODES } from "@repo/shared";

/**
 * Check a single newly added/updated item and create alerts.
 */
export async function checkItem(
  itemId: string,
  sectionId: string,
  quotationId: string,
  projectId: string
) {
  // Load project context
  const [proj] = await db
    .select()
    .from(project)
    .where(eq(project.id, projectId));
  if (!proj) return [];

  // Load the item
  const [item] = await db
    .select()
    .from(quotationItem)
    .where(eq(quotationItem.id, itemId));
  if (!item) return [];

  // Load the section to get trade code
  const [section] = await db
    .select()
    .from(quotationSection)
    .where(eq(quotationSection.id, sectionId));
  if (!section) return [];

  // Load ALL items across all sections for cross-reference
  const sections = await db
    .select()
    .from(quotationSection)
    .where(eq(quotationSection.quotationId, quotationId));

  const allItems: Record<string, { name: string; unit: string; quantity: number; tradeCode: string }[]> = {};
  for (const s of sections) {
    const items = await db
      .select()
      .from(quotationItem)
      .where(eq(quotationItem.sectionId, s.id));
    allItems[s.tradeCode] = items.map((i) => ({
      name: i.name,
      unit: i.unit,
      quantity: i.quantity,
      tradeCode: s.tradeCode,
    }));
  }

  const matched = await matchItemRules(
    { name: item.name, unit: item.unit, quantity: item.quantity, tradeCode: section.tradeCode },
    {
      projectType: proj.type as "residential" | "commercial",
      ageTier: proj.ageTier,
      hasElevator: proj.hasElevator,
      area: proj.area,
    },
    allItems
  );

  // Create alerts (avoid duplicates)
  const newAlerts = [];
  for (const m of matched) {
    // Check if same rule+quotation already has a pending/accepted/ignored alert
    const [existing] = await db
      .select()
      .from(alert)
      .where(
        and(
          eq(alert.quotationId, quotationId),
          eq(alert.ruleId, m.ruleId)
        )
      );
    if (existing) continue;

    // Determine which section this alert belongs to
    const targetSectionId = m.actionTrade
      ? sections.find((s) => s.tradeCode === m.actionTrade)?.id ?? sectionId
      : sectionId;

    const [newAlert] = await db
      .insert(alert)
      .values({
        quotationId,
        sectionId: targetSectionId,
        source: "rule",
        ruleId: m.ruleId,
        triggerItemId: itemId,
        severity: m.severity,
        message: m.message,
        suggestion: m.actionItem,
        status: "pending",
      })
      .returning();

    newAlerts.push(newAlert);
  }

  return newAlerts;
}

/**
 * Check condition-type rules when entering a section (called once, not per-item).
 */
export async function checkSectionEntry(
  sectionId: string,
  quotationId: string,
  projectId: string
) {
  const [proj] = await db.select().from(project).where(eq(project.id, projectId));
  if (!proj) return [];

  const [section] = await db.select().from(quotationSection).where(eq(quotationSection.id, sectionId));
  if (!section) return [];

  const sections = await db.select().from(quotationSection).where(eq(quotationSection.quotationId, quotationId));
  const allItems: Record<string, { name: string; unit: string; quantity: number; tradeCode: string }[]> = {};
  for (const s of sections) {
    const items = await db.select().from(quotationItem).where(eq(quotationItem.sectionId, s.id));
    allItems[s.tradeCode] = items.map((i) => ({ name: i.name, unit: i.unit, quantity: i.quantity, tradeCode: s.tradeCode }));
  }

  const matched = await checkSectionConditions(
    section.tradeCode,
    { projectType: proj.type as "residential" | "commercial", ageTier: proj.ageTier, hasElevator: proj.hasElevator, area: proj.area },
    allItems
  );

  const newAlerts = [];
  for (const m of matched) {
    const [existing] = await db.select().from(alert).where(and(eq(alert.quotationId, quotationId), eq(alert.ruleId, m.ruleId)));
    if (existing) continue;

    const targetSectionId = m.actionTrade
      ? sections.find((s) => s.tradeCode === m.actionTrade)?.id ?? sectionId
      : sectionId;

    const [newAlert] = await db.insert(alert).values({
      quotationId, sectionId: targetSectionId, source: "rule", ruleId: m.ruleId,
      triggerItemId: null, severity: m.severity, message: m.message, suggestion: m.actionItem, status: "pending",
    }).returning();
    newAlerts.push(newAlert);
  }
  return newAlerts;
}

/**
 * Cross-trade check: re-evaluate dependency/linked rules across all sections.
 */
export async function crossTradeCheck(
  quotationId: string,
  projectId: string
) {
  const [proj] = await db
    .select()
    .from(project)
    .where(eq(project.id, projectId));
  if (!proj) return [];

  const sections = await db
    .select()
    .from(quotationSection)
    .where(eq(quotationSection.quotationId, quotationId));

  // Collect all items
  const allItems: Record<string, { name: string; unit: string; quantity: number; tradeCode: string }[]> = {};
  for (const s of sections) {
    const items = await db
      .select()
      .from(quotationItem)
      .where(eq(quotationItem.sectionId, s.id));
    allItems[s.tradeCode] = items.map((i) => ({
      name: i.name,
      unit: i.unit,
      quantity: i.quantity,
      tradeCode: s.tradeCode,
    }));
  }

  // Re-check every item against dependency/linked rules
  const newAlerts = [];
  for (const s of sections) {
    const items = allItems[s.tradeCode] || [];
    for (const item of items) {
      const matched = await matchItemRules(
        item,
        {
          projectType: proj.type as "residential" | "commercial",
          ageTier: proj.ageTier,
          hasElevator: proj.hasElevator,
          area: proj.area,
        },
        allItems
      );

      for (const m of matched) {
        if (m.type !== "dependency" && m.type !== "linked") continue;

        const [existing] = await db
          .select()
          .from(alert)
          .where(
            and(eq(alert.quotationId, quotationId), eq(alert.ruleId, m.ruleId))
          );
        if (existing) continue;

        const targetSectionId = m.actionTrade
          ? sections.find((sec) => sec.tradeCode === m.actionTrade)?.id ?? s.id
          : s.id;

        const [newAlert] = await db
          .insert(alert)
          .values({
            quotationId,
            sectionId: targetSectionId,
            source: "rule",
            ruleId: m.ruleId,
            triggerItemId: null,
            severity: m.severity,
            message: m.message,
            suggestion: m.actionItem,
            status: "pending",
          })
          .returning();

        newAlerts.push(newAlert);
      }
    }
  }

  return newAlerts;
}
```

- [ ] **Step 3: Create guardian router**

```typescript
// nooko-quotation-guardian/packages/api/src/routers/guardian.ts
import { z } from "zod";
import { router, protectedProcedure } from "../trpc";
import { checkItem, checkSectionEntry, crossTradeCheck } from "../services/guardian-engine";

export const guardianRouter = router({
  checkItem: protectedProcedure
    .input(
      z.object({
        itemId: z.string(),
        sectionId: z.string(),
        quotationId: z.string(),
        projectId: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      return checkItem(
        input.itemId,
        input.sectionId,
        input.quotationId,
        input.projectId
      );
    }),

  checkSectionEntry: protectedProcedure
    .input(
      z.object({
        sectionId: z.string(),
        quotationId: z.string(),
        projectId: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      return checkSectionEntry(input.sectionId, input.quotationId, input.projectId);
    }),

  crossTradeCheck: protectedProcedure
    .input(
      z.object({
        quotationId: z.string(),
        projectId: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      return crossTradeCheck(input.quotationId, input.projectId);
    }),
});
```

- [ ] **Step 4: Add guardian router to root**

Update `packages/api/src/routers/index.ts` — add:
```typescript
import { guardianRouter } from "./guardian";
// in router({...}):
guardian: guardianRouter,
```

- [ ] **Step 5: Typecheck**

```bash
cd /Users/stephenkao/Nooko_Your_InteriorDeco_Ai/nooko-quotation-guardian
bun run typecheck
```

- [ ] **Step 6: Commit**

```bash
git add nooko-quotation-guardian/packages/api/src/services/ nooko-quotation-guardian/packages/api/src/routers/guardian.ts
git commit -m "feat: add Guardian Engine with rule matcher and cross-trade checker"
```

---

## Task 7: Frontend — Project List & Create Page

**Files:**
- Create: `nooko-quotation-guardian/apps/web/src/routes/projects/index.tsx`
- Create: `nooko-quotation-guardian/apps/web/src/routes/projects/new.tsx`
- Create: `nooko-quotation-guardian/apps/web/src/components/project/ProjectCard.tsx`
- Create: `nooko-quotation-guardian/apps/web/src/components/project/SiteConditionForm.tsx`
- Create: `nooko-quotation-guardian/apps/web/src/constants/trades.ts`

- [ ] **Step 1: Create SiteConditionForm**

Note: Frontend imports trade constants directly from `@repo/shared` — no wrapper file needed.

```typescript
// nooko-quotation-guardian/apps/web/src/components/project/SiteConditionForm.tsx
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface SiteConditionFormData {
  name: string;
  type: "residential" | "commercial";
  ageTier: number | null;
  area: number;
  floor: number;
  hasElevator: boolean;
}

interface Props {
  onSubmit: (data: SiteConditionFormData) => void;
  isLoading?: boolean;
}

export function SiteConditionForm({ onSubmit, isLoading }: Props) {
  const form = useForm<SiteConditionFormData>({
    defaultValues: {
      name: "",
      type: "residential",
      ageTier: 0,
      area: 30,
      floor: 1,
      hasElevator: false,
    },
  });

  const projectType = form.watch("type");

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 max-w-lg">
      <div className="space-y-2">
        <Label htmlFor="name">案件名稱</Label>
        <Input id="name" {...form.register("name", { required: true })} placeholder="例：王先生信義路住宅" />
      </div>

      <div className="space-y-2">
        <Label>物件型態</Label>
        <Select
          value={form.watch("type")}
          onValueChange={(v) => form.setValue("type", v as "residential" | "commercial")}
        >
          <SelectTrigger><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="residential">住宅</SelectItem>
            <SelectItem value="commercial">商辦</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {projectType === "residential" && (
        <div className="space-y-2">
          <Label>屋齡區間</Label>
          <Select
            value={String(form.watch("ageTier") ?? 0)}
            onValueChange={(v) => form.setValue("ageTier", Number(v))}
          >
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="0">0-5 年（新成屋）</SelectItem>
              <SelectItem value="5">5-10 年</SelectItem>
              <SelectItem value="10">10-20 年（中古屋）</SelectItem>
              <SelectItem value="20">20-30 年</SelectItem>
              <SelectItem value="30">30 年以上（老屋）</SelectItem>
            </SelectContent>
          </Select>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="area">坪數</Label>
          <Input id="area" type="number" {...form.register("area", { valueAsNumber: true })} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="floor">樓層</Label>
          <Input id="floor" type="number" {...form.register("floor", { valueAsNumber: true })} />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="hasElevator"
          {...form.register("hasElevator")}
          className="h-4 w-4"
        />
        <Label htmlFor="hasElevator">有電梯</Label>
      </div>

      <Button type="submit" disabled={isLoading} className="w-full">
        {isLoading ? "建立中..." : "建立案件"}
      </Button>
    </form>
  );
}
```

- [ ] **Step 2: Create project list page and new project page**

Create route files at:
- `apps/web/src/routes/projects/index.tsx` — lists projects with cards, link to `/projects/new`
- `apps/web/src/routes/projects/new.tsx` — renders SiteConditionForm, on submit calls `trpc.project.create.mutate()`, then navigates to `/quotation/$projectId`

Follow TanStack Router file-based routing conventions (check the scaffolded `__root.tsx` for the exact pattern — `createFileRoute` or `createLazyFileRoute`).

- [ ] **Step 3: Verify page renders**

```bash
cd /Users/stephenkao/Nooko_Your_InteriorDeco_Ai/nooko-quotation-guardian
bun run dev
```

Open http://localhost:3000/projects/new — form should render.

- [ ] **Step 4: Commit**

```bash
git add nooko-quotation-guardian/apps/web/
git commit -m "feat: add project list and create pages"
```

---

## Task 8: Frontend — Three-Column Quotation Page

**Files:**
- Create: `nooko-quotation-guardian/apps/web/src/routes/quotation/$projectId.tsx`
- Create: `nooko-quotation-guardian/apps/web/src/components/quotation/TradeStepper.tsx`
- Create: `nooko-quotation-guardian/apps/web/src/components/quotation/StepperItem.tsx`
- Create: `nooko-quotation-guardian/apps/web/src/components/quotation/ItemTable.tsx`
- Create: `nooko-quotation-guardian/apps/web/src/components/quotation/ItemRow.tsx`
- Create: `nooko-quotation-guardian/apps/web/src/components/quotation/AddItemRow.tsx`
- Create: `nooko-quotation-guardian/apps/web/src/components/quotation/SectionNav.tsx`
- Create: `nooko-quotation-guardian/apps/web/src/components/quotation/AlertPanel.tsx`
- Create: `nooko-quotation-guardian/apps/web/src/components/quotation/AlertCard.tsx`
- Create: `nooko-quotation-guardian/apps/web/src/components/quotation/GateStatus.tsx`

This is the core page. Build it in sub-steps:

- [ ] **Step 1: Create the route with three-column layout shell**

`apps/web/src/routes/quotation/$projectId.tsx` — the main page:
- Load project + quotation + sections via tRPC queries
- State: `currentSectionIndex` (number)
- Layout: `flex h-screen` with three columns:
  - Left (w-56): TradeStepper
  - Center (flex-1): ItemTable + SectionNav
  - Right (w-72): AlertPanel

- [ ] **Step 2: Create TradeStepper + StepperItem**

`TradeStepper.tsx`:
- Receives: sections array, currentIndex, pending alert counts per section
- Renders: vertical stepper with StepperItem for each section
- Progress bar at bottom: `{completed} / 13 工種`

`StepperItem.tsx`:
- Props: tradeCode, displayName, status, pendingAlertCount, isCurrent, onClick
- Visual states: ✓ green (completed), blue highlight (current/editing), gray (pending)
- Red badge if pendingAlertCount > 0

- [ ] **Step 3: Create ItemTable + ItemRow + AddItemRow**

`ItemTable.tsx`:
- Receives: sectionId, items, alerts
- Columns: 工項名稱 / 單位 / 數量 / 狀態(icon) / 操作(delete)
- Maps each item to an ItemRow

`ItemRow.tsx`:
- Editable inline (click to edit name/unit/quantity)
- Status icon: ✓ (rule passed), ⚠ (triggered alert), — (no rule)
- On blur/enter: calls `trpc.item.update` then `trpc.guardian.checkItem`
- Red left border if item has triggered a pending alert

`AddItemRow.tsx`:
- Empty row with "+" button
- On submit: calls `trpc.item.create` then `trpc.guardian.checkItem`

- [ ] **Step 4: Create SectionNav**

`SectionNav.tsx`:
- Previous/Next trade buttons
- Next button: disabled if there are pending alerts for current section (soft gate)
- Badge on Next showing pending alert count
- On click Next: calls `trpc.guardian.crossTradeCheck`, updates section status

- [ ] **Step 5: Create AlertPanel + AlertCard + GateStatus**

`AlertPanel.tsx`:
- Receives: alerts for current section
- Split into: ActiveAlerts (pending) and ResolvedAlerts (accepted/ignored, grayed)
- GateStatus summary at bottom

`AlertCard.tsx`:
- Shows: severity color, message, trigger source
- Two buttons: "加入" (accept) and "忽略" (ignore)
- "忽略" opens a dialog requiring reason text
- On accept: calls `trpc.alert.accept`
- On ignore: calls `trpc.alert.ignore`

`GateStatus.tsx`:
- Shows: `尚有 N 項提醒未處理` or `所有提醒已處理 ✓`

- [ ] **Step 6: Apply minimalist design style**

- Use neutral, low-saturation colors (gray-50 to gray-900 palette)
- Generous whitespace (p-6, gap-4)
- Clear visual hierarchy via font weight and size, not color
- Alert severity: subtle left border (red-500 or amber-500), not full background fill
- Avoid decorative elements

- [ ] **Step 7: Verify full flow**

```bash
cd /Users/stephenkao/Nooko_Your_InteriorDeco_Ai/nooko-quotation-guardian
bun run dev
```

Test: Create project → navigate to quotation page → add items → see alerts → accept/ignore → navigate between trades.

- [ ] **Step 8: Commit**

```bash
git add nooko-quotation-guardian/apps/web/src/
git commit -m "feat: add three-column quotation page with stepper, table, and alerts"
```

---

## Task 9: Gemini Final Scan

**Files:**
- Create: `nooko-quotation-guardian/server/src/services/gemini-scanner.ts`
- Modify: `nooko-quotation-guardian/packages/api/src/routers/guardian.ts`
- Create: `nooko-quotation-guardian/apps/web/src/components/final-scan/FinalScanView.tsx`

- [ ] **Step 1: Create gemini-scanner.ts**

```typescript
// nooko-quotation-guardian/server/src/services/gemini-scanner.ts
import { GoogleGenAI } from "@google/genai";

const genai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY ?? "" });

interface ScanInput {
  projectType: string;
  ageTier: number | null;
  area: number;
  floor: number;
  hasElevator: boolean;
  sections: {
    tradeCode: string;
    tradeName: string;
    items: { name: string; unit: string; quantity: number }[];
  }[];
}

interface ScanResult {
  message: string;
  suggestion: string | null;
  severity: "red" | "yellow";
  confidence: number;
  reasoning: string;
  targetTradeCode: string;
}

export async function runFinalScan(input: ScanInput): Promise<ScanResult[]> {
  const itemSummary = input.sections
    .map(
      (s) =>
        `【${s.tradeName}】\n${s.items.map((i) => `  - ${i.name} (${i.quantity} ${i.unit})`).join("\n") || "  （無工項）"}`
    )
    .join("\n\n");

  const prompt = `你是台灣室內裝修報價審核專家。以下是一份裝修報價單，請檢查是否有遺漏、衝突、或不合理之處。

案件資訊：
- 型態：${input.projectType === "residential" ? "住宅" : "商辦"}
- 屋齡：${input.ageTier !== null ? `${input.ageTier} 年以上` : "不適用"}
- 坪數：${input.area} 坪
- 樓層：${input.floor} 樓
- 電梯：${input.hasElevator ? "有" : "無"}

報價內容：
${itemSummary}

請以 JSON 陣列回覆，每個問題包含：
- message: 問題描述（繁體中文）
- suggestion: 建議補充的工項名稱（若適用，否則 null）
- severity: "red"（必要）或 "yellow"（建議）
- confidence: 0-1 的信心分數
- reasoning: 判斷理由
- targetTradeCode: 該問題歸屬的工種 code

只回覆 JSON，不要其他文字。如果沒有問題，回覆空陣列 []。`;

  try {
    const response = await genai.models.generateContent({
      model: "gemini-2.0-flash",
      contents: prompt,
    });

    const text = response.text?.trim() ?? "[]";
    // Strip markdown code fence if present
    const json = text.replace(/^```json?\n?/, "").replace(/\n?```$/, "");
    return JSON.parse(json) as ScanResult[];
  } catch (error) {
    console.error("Gemini scan failed:", error);
    return [];
  }
}
```

- [ ] **Step 2: Add finalScan to guardian router**

Add to `packages/api/src/routers/guardian.ts`:

```typescript
import { runFinalScan } from "../../../../server/src/services/gemini-scanner"; // server/ is the one exception — Gemini is infra, not business logic
import { TRADE_DISPLAY_NAMES } from "@repo/shared";

// Add to guardianRouter:
finalScan: protectedProcedure
  .input(z.object({ quotationId: z.string(), projectId: z.string() }))
  .mutation(async ({ ctx, input }) => {
    const [proj] = await ctx.db.select().from(project).where(eq(project.id, input.projectId));
    if (!proj) throw new Error("Project not found");

    const sections = await ctx.db.select().from(quotationSection)
      .where(eq(quotationSection.quotationId, input.quotationId))
      .orderBy(quotationSection.sortOrder);

    const sectionData = [];
    for (const s of sections) {
      const items = await ctx.db.select().from(quotationItem)
        .where(eq(quotationItem.sectionId, s.id));
      sectionData.push({
        tradeCode: s.tradeCode,
        tradeName: TRADE_DISPLAY_NAMES[s.tradeCode as keyof typeof TRADE_DISPLAY_NAMES] ?? s.tradeCode,
        items: items.map((i) => ({ name: i.name, unit: i.unit, quantity: i.quantity })),
      });
    }

    // Run cross-trade check first
    const crossAlerts = await crossTradeCheck(input.quotationId, input.projectId);

    // Run Gemini scan
    const geminiResults = await runFinalScan({
      projectType: proj.type,
      ageTier: proj.ageTier,
      area: proj.area,
      floor: proj.floor,
      hasElevator: proj.hasElevator,
      sections: sectionData,
    });

    // Create alerts from Gemini results
    const geminiAlerts = [];
    for (const r of geminiResults) {
      const targetSection = sections.find((s) => s.tradeCode === r.targetTradeCode);
      if (!targetSection) continue;

      const [newAlert] = await ctx.db.insert(alert).values({
        quotationId: input.quotationId,
        sectionId: targetSection.id,
        source: "gemini",
        severity: r.severity,
        message: r.message,
        suggestion: r.suggestion,
        aiConfidence: r.confidence,
        aiReasoning: r.reasoning,
        status: "pending",
      }).returning();

      geminiAlerts.push(newAlert);
    }

    return { crossAlerts, geminiAlerts };
  }),
```

Note: add necessary imports (`project`, `quotationSection`, `quotationItem`, `alert` from schema, `eq` from drizzle-orm).

- [ ] **Step 3: Create FinalScanView component**

`apps/web/src/components/final-scan/FinalScanView.tsx`:
- Rendered inside the QuotationPage as a virtual "14th step" after all 13 trades are completed
- When the last trade (cleaning) is completed and user clicks next, the center panel switches to FinalScanView
- Button to trigger final scan (`trpc.guardian.finalScan`)
- Loading state while Gemini processes
- Display results grouped by trade, showing both cross-trade and Gemini alerts
- Same AlertCard accept/ignore UI as the main page
- "匯出 Excel" button at bottom (disabled until all alerts resolved)

- [ ] **Step 4: Commit**

```bash
git add nooko-quotation-guardian/
git commit -m "feat: add Gemini final scan and FinalScanView"
```

---

## Task 10: Excel Export

**Files:**
- Create: `nooko-quotation-guardian/packages/api/src/services/excel-exporter.ts`
- Modify: `nooko-quotation-guardian/packages/api/src/routers/quotation.ts`

Note: `xlsx` is installed in `server/` — add it to `packages/api/package.json` as well, or move the dependency.

- [ ] **Step 1: Create excel-exporter.ts**

```typescript
// nooko-quotation-guardian/packages/api/src/services/excel-exporter.ts
import XLSX from "xlsx";
import { TRADE_DISPLAY_NAMES } from "@repo/shared";

interface ExportSection {
  tradeCode: string;
  items: { name: string; unit: string; quantity: number }[];
}

export function generateExcel(
  projectName: string,
  sections: ExportSection[]
): Buffer {
  const wb = XLSX.utils.book_new();

  const rows: (string | number)[][] = [];
  rows.push(["報價單", projectName]);
  rows.push([]);

  for (const section of sections) {
    const tradeName =
      TRADE_DISPLAY_NAMES[section.tradeCode as keyof typeof TRADE_DISPLAY_NAMES] ??
      section.tradeCode;
    rows.push([tradeName]);
    rows.push(["工項", "單位", "數量"]);
    for (const item of section.items) {
      rows.push([item.name, item.unit, item.quantity]);
    }
    rows.push([]);
  }

  const ws = XLSX.utils.aoa_to_sheet(rows);
  XLSX.utils.book_append_sheet(wb, ws, "報價單");

  return Buffer.from(XLSX.write(wb, { type: "buffer", bookType: "xlsx" }));
}
```

- [ ] **Step 2: Add export endpoint to quotation router**

Add to `packages/api/src/routers/quotation.ts`:

```typescript
export: protectedProcedure
  .input(z.object({ projectId: z.string() }))
  .mutation(async ({ ctx, input }) => {
    // Load project, quotation, sections, items
    // Call generateExcel()
    // Return base64 encoded buffer
    // Update quotation.exportedAt
  }),
```

- [ ] **Step 3: Frontend download trigger**

In FinalScanView, the "匯出 Excel" button calls the export mutation, decodes base64, and triggers browser download.

- [ ] **Step 4: Commit**

```bash
git add nooko-quotation-guardian/
git commit -m "feat: add Excel export for quotation"
```

---

## Task 11: Auth Pages (Login / Register)

**Files:**
- Modify: `nooko-quotation-guardian/apps/web/src/routes/login.tsx`
- Modify: `nooko-quotation-guardian/apps/web/src/routes/__root.tsx` (add auth guard)

The Better-T Stack scaffold likely already includes login/register pages and Better-Auth integration. In this task:

- [ ] **Step 1: Verify auth pages exist from scaffold**

Check `apps/web/src/routes/login.tsx` and auth-related components. If they exist, customize the styling to match the minimalist design.

- [ ] **Step 2: Add auth guard to protected routes**

In `__root.tsx` or a layout route, redirect unauthenticated users to `/login`. Protected routes: `/projects/*`, `/quotation/*`.

- [ ] **Step 3: Test login flow**

```bash
bun run dev
```

Register a user → login → should redirect to `/projects`.

- [ ] **Step 4: Commit**

```bash
git add nooko-quotation-guardian/apps/web/
git commit -m "feat: configure auth pages and route protection"
```

---

## Task 12: End-to-End Smoke Test

- [ ] **Step 1: Start the full stack**

```bash
cd /Users/stephenkao/Nooko_Your_InteriorDeco_Ai/nooko-quotation-guardian
bun run dev
```

- [ ] **Step 2: Full user flow test**

1. Register / login
2. Create project (住宅, 25年, 30坪, 5F, 有電梯)
3. Navigate to quotation page — 13 工種 stepper visible
4. Enter 保護工程 — should see condition alert (電梯保護, 公共區域保護)
5. Accept one, ignore one with reason
6. Navigate to 拆除工程 — add "天花板拆除" and "地磚拆除（打見底）"
7. Should see alerts: 垃圾清運、地面整平、防水施作
8. Process all alerts
9. Move to next trade — soft gate should work
10. After filling enough trades, run final scan
11. Process Gemini alerts
12. Export Excel — file downloads

- [ ] **Step 3: Fix any issues found**

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete MVP quotation guardian system"
```

---

## Dependency Graph

```
Task 1 (Scaffold)
  └─→ Task 2 (Shared Package)
       └─→ Task 3 (DB Schema)
            ├─→ Task 4 (Seed Rules)
            └─→ Task 5 (tRPC Routers)
                 └─→ Task 6 (Guardian Engine)
                      ├─→ Task 7 (Frontend: Projects)
                      │    └─→ Task 8 (Frontend: Quotation Page)
                      │         └─→ Task 9 (Gemini Final Scan)
                      │              └─→ Task 10 (Excel Export)
                      └─→ Task 11 (Auth Pages) [can parallel with 7-10]

Task 12 (E2E Test) depends on all above
```

Tasks 7-10 are sequential (each builds on the previous). Task 11 can run in parallel with Tasks 7-10 since auth scaffold already exists.
