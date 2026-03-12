import { z } from "zod";
import { TRPCError } from "@trpc/server";
import { router, orgProtectedProcedure } from "../index";
import { db } from "@my-better-t-app/db";
import { rule, alertResponse } from "@my-better-t-app/db/schema/house-iq";
import { eq, and } from "drizzle-orm";
import { checkAllRulesForQuotation } from "../lib/rule-engine";

export const rulesRouter = router({
  /** Check all rules for a given quotation */
  check: orgProtectedProcedure
    .input(z.object({ quotationId: z.string() }))
    .query(async ({ ctx, input }) => {
      return checkAllRulesForQuotation(input.quotationId, ctx.organizationId);
    }),

  /** Record designer's response to an alert */
  respond: orgProtectedProcedure
    .input(
      z.object({
        quotationItemId: z.string(),
        ruleId: z.string(),
        response: z.enum(["accepted", "dismissed", "added_item"]),
      }),
    )
    .mutation(async ({ ctx, input }) => {
      const [resp] = await db
        .insert(alertResponse)
        .values({
          quotationItemId: input.quotationItemId,
          ruleId: input.ruleId,
          userId: ctx.session.user.id,
          response: input.response,
        })
        .returning();
      return resp;
    }),

  /** List global rules (visible to all) */
  listGlobal: orgProtectedProcedure.query(async () => {
    return db.query.rule.findMany({
      where: and(eq(rule.scope, "global"), eq(rule.isActive, true)),
    });
  }),

  /** List company-specific rules for the current organization */
  listCompany: orgProtectedProcedure.query(async ({ ctx }) => {
    return db.query.rule.findMany({
      where: and(
        eq(rule.scope, "company"),
        eq(rule.organizationId, ctx.organizationId),
      ),
    });
  }),

  /** Create a company-specific rule */
  createCompany: orgProtectedProcedure
    .input(
      z.object({
        triggerWbs: z.string().min(1),
        relatedWbs: z.string().min(1),
        ruleType: z.enum(["dependency", "conflict", "threshold"]),
        message: z.string().min(1),
        severity: z.enum(["warning", "critical"]),
      }),
    )
    .mutation(async ({ ctx, input }) => {
      const [newRule] = await db
        .insert(rule)
        .values({
          ...input,
          organizationId: ctx.organizationId,
          scope: "company",
          source: "manual",
        })
        .returning();
      return newRule;
    }),

  /** Toggle a company rule's active status */
  toggle: orgProtectedProcedure
    .input(z.object({ id: z.string(), isActive: z.boolean() }))
    .mutation(async ({ ctx, input }) => {
      // Only allow toggling company rules owned by this org
      const existing = await db.query.rule.findFirst({
        where: and(
          eq(rule.id, input.id),
          eq(rule.organizationId, ctx.organizationId),
        ),
      });
      if (!existing) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Rule not found or not owned by your organization",
        });
      }

      const [updated] = await db
        .update(rule)
        .set({ isActive: input.isActive })
        .where(eq(rule.id, input.id))
        .returning();
      return updated;
    }),
});
