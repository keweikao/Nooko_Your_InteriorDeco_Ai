import { relations } from "drizzle-orm";
import {
  pgTable,
  text,
  timestamp,
  boolean,
  real,
  integer,
  pgEnum,
  index,
} from "drizzle-orm/pg-core";
import { organization, user } from "./auth";

// ─── Enums ───────────────────────────────────────────────────────────────────

export const quotationStatusEnum = pgEnum("quotation_status", [
  "draft",
  "reviewing",
  "completed",
]);

export const ruleTypeEnum = pgEnum("rule_type", [
  "dependency",
  "conflict",
  "threshold",
]);

export const ruleSeverityEnum = pgEnum("rule_severity", [
  "warning",
  "critical",
]);

export const ruleScopeEnum = pgEnum("rule_scope", ["global", "company"]);

export const ruleSourceEnum = pgEnum("rule_source", [
  "manual",
  "ai_suggested",
  "learned",
]);

export const alertResponseTypeEnum = pgEnum("alert_response_type", [
  "accepted",
  "dismissed",
  "added_item",
]);

// ─── WBS Tags (標準工項分類) ─────────────────────────────────────────────────

export const wbsTag = pgTable("wbs_tag", {
  id: text("id")
    .primaryKey()
    .$defaultFn(() => crypto.randomUUID()),
  code: text("code").notNull().unique(),
  category: text("category").notNull(),
  nameTw: text("name_tw").notNull(),
  description: text("description"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// ─── Rules (統一規則表：通用 + 公司專屬) ─────────────────────────────────────

export const rule = pgTable(
  "rule",
  {
    id: text("id")
      .primaryKey()
      .$defaultFn(() => crypto.randomUUID()),
    organizationId: text("organization_id").references(() => organization.id, {
      onDelete: "cascade",
    }),
    scope: ruleScopeEnum("scope").notNull().default("global"),
    triggerWbs: text("trigger_wbs").notNull(),
    relatedWbs: text("related_wbs").notNull(),
    ruleType: ruleTypeEnum("rule_type").notNull().default("dependency"),
    message: text("message").notNull(),
    severity: ruleSeverityEnum("severity").notNull().default("warning"),
    source: ruleSourceEnum("source").notNull().default("manual"),
    isActive: boolean("is_active").notNull().default(true),
    confidence: real("confidence").default(1.0),
    createdAt: timestamp("created_at").defaultNow().notNull(),
  },
  (table) => [
    index("rule_trigger_wbs_idx").on(table.triggerWbs),
    index("rule_organization_id_idx").on(table.organizationId),
    index("rule_scope_active_idx").on(table.scope, table.isActive),
  ],
);

// ─── Quotations (報價單) ─────────────────────────────────────────────────────

export const quotation = pgTable(
  "quotation",
  {
    id: text("id")
      .primaryKey()
      .$defaultFn(() => crypto.randomUUID()),
    organizationId: text("organization_id")
      .notNull()
      .references(() => organization.id, { onDelete: "cascade" }),
    createdBy: text("created_by")
      .notNull()
      .references(() => user.id),
    projectName: text("project_name").notNull(),
    projectAddress: text("project_address"),
    status: quotationStatusEnum("status").notNull().default("draft"),
    createdAt: timestamp("created_at").defaultNow().notNull(),
    updatedAt: timestamp("updated_at")
      .defaultNow()
      .notNull()
      .$onUpdate(() => new Date()),
  },
  (table) => [
    index("quotation_organization_id_idx").on(table.organizationId),
    index("quotation_created_by_idx").on(table.createdBy),
  ],
);

// ─── Quotation Items (報價工項) ──────────────────────────────────────────────

export const quotationItem = pgTable(
  "quotation_item",
  {
    id: text("id")
      .primaryKey()
      .$defaultFn(() => crypto.randomUUID()),
    quotationId: text("quotation_id")
      .notNull()
      .references(() => quotation.id, { onDelete: "cascade" }),
    category: text("category").notNull(),
    itemName: text("item_name").notNull(),
    wbsCode: text("wbs_code"),
    unit: text("unit").notNull(),
    quantity: real("quantity").notNull().default(1),
    sortOrder: integer("sort_order").notNull().default(0),
    createdAt: timestamp("created_at").defaultNow().notNull(),
  },
  (table) => [
    index("quotation_item_quotation_id_idx").on(table.quotationId),
    index("quotation_item_wbs_code_idx").on(table.wbsCode),
  ],
);

// ─── Alert Responses (設計師回饋) ────────────────────────────────────────────

export const alertResponse = pgTable(
  "alert_response",
  {
    id: text("id")
      .primaryKey()
      .$defaultFn(() => crypto.randomUUID()),
    quotationItemId: text("quotation_item_id")
      .notNull()
      .references(() => quotationItem.id, { onDelete: "cascade" }),
    ruleId: text("rule_id")
      .notNull()
      .references(() => rule.id),
    userId: text("user_id")
      .notNull()
      .references(() => user.id),
    response: alertResponseTypeEnum("response").notNull(),
    createdAt: timestamp("created_at").defaultNow().notNull(),
  },
  (table) => [
    index("alert_response_rule_id_idx").on(table.ruleId),
    index("alert_response_quotation_item_id_idx").on(table.quotationItemId),
  ],
);

// ─── Relations ───────────────────────────────────────────────────────────────

export const ruleRelations = relations(rule, ({ one }) => ({
  organization: one(organization, {
    fields: [rule.organizationId],
    references: [organization.id],
  }),
}));

export const quotationRelations = relations(quotation, ({ one, many }) => ({
  organization: one(organization, {
    fields: [quotation.organizationId],
    references: [organization.id],
  }),
  createdByUser: one(user, {
    fields: [quotation.createdBy],
    references: [user.id],
  }),
  items: many(quotationItem),
}));

export const quotationItemRelations = relations(
  quotationItem,
  ({ one, many }) => ({
    quotation: one(quotation, {
      fields: [quotationItem.quotationId],
      references: [quotation.id],
    }),
    alertResponses: many(alertResponse),
  }),
);

export const alertResponseRelations = relations(alertResponse, ({ one }) => ({
  quotationItem: one(quotationItem, {
    fields: [alertResponse.quotationItemId],
    references: [quotationItem.id],
  }),
  rule: one(rule, {
    fields: [alertResponse.ruleId],
    references: [rule.id],
  }),
  user: one(user, {
    fields: [alertResponse.userId],
    references: [user.id],
  }),
}));
