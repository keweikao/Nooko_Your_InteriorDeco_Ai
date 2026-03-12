import { db } from "@my-better-t-app/db";
import {
  rule,
  quotationItem,
} from "@my-better-t-app/db/schema/house-iq";
import { eq, and } from "drizzle-orm";

export type Alert = {
  ruleId: string;
  message: string;
  severity: "warning" | "critical";
  relatedWbs: string;
  scope: "global" | "company";
  source: "manual" | "ai_suggested" | "learned";
  confidence: number | null;
  triggerItemId: string;
  triggerItemName: string;
};

/**
 * Check rules triggered by a single quotation item.
 * 1. Match rules where trigger_wbs = item.wbsCode
 * 2. Filter: company rules for this org + global rules
 * 3. Check if related item already exists in quotation
 * 4. Return alerts for missing related items
 */
export async function checkRulesForItem(
  item: { id: string; wbsCode: string | null; itemName: string },
  quotationId: string,
  organizationId: string,
): Promise<Alert[]> {
  if (!item.wbsCode) return [];

  // Find all active rules matching this WBS trigger
  const matchingRules = await db.query.rule.findMany({
    where: and(eq(rule.triggerWbs, item.wbsCode), eq(rule.isActive, true)),
  });

  // Filter to relevant rules: company rules for this org + global rules
  const relevantRules = matchingRules.filter(
    (r) =>
      r.scope === "global" ||
      (r.scope === "company" && r.organizationId === organizationId),
  );

  // Sort: company rules first (higher priority), then by confidence desc
  relevantRules.sort((a, b) => {
    if (a.scope !== b.scope) {
      return a.scope === "company" ? -1 : 1;
    }
    return (b.confidence ?? 0) - (a.confidence ?? 0);
  });

  // Get existing WBS codes in this quotation
  const existingItems = await db.query.quotationItem.findMany({
    where: eq(quotationItem.quotationId, quotationId),
  });
  const existingWbsCodes = new Set(
    existingItems.map((i) => i.wbsCode).filter(Boolean),
  );

  // Generate alerts for missing related items
  return relevantRules
    .filter((r) => !existingWbsCodes.has(r.relatedWbs))
    .map((r) => ({
      ruleId: r.id,
      message: r.message,
      severity: r.severity,
      relatedWbs: r.relatedWbs,
      scope: r.scope,
      source: r.source,
      confidence: r.confidence,
      triggerItemId: item.id,
      triggerItemName: item.itemName,
    }));
}

/**
 * Check all rules for all items in a quotation.
 * Used to get a full report of all triggered alerts.
 */
export async function checkAllRulesForQuotation(
  quotationId: string,
  organizationId: string,
): Promise<Alert[]> {
  const items = await db.query.quotationItem.findMany({
    where: eq(quotationItem.quotationId, quotationId),
  });

  const allAlerts: Alert[] = [];
  for (const item of items) {
    if (item.wbsCode) {
      const alerts = await checkRulesForItem(item, quotationId, organizationId);
      allAlerts.push(...alerts);
    }
  }

  // Deduplicate: same rule + same relatedWbs should only appear once
  const seen = new Set<string>();
  return allAlerts.filter((a) => {
    const key = `${a.ruleId}-${a.relatedWbs}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}
