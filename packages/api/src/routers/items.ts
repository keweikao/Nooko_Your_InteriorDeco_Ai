import { z } from "zod";
import { TRPCError } from "@trpc/server";
import { router, orgProtectedProcedure } from "../index";
import { db } from "@my-better-t-app/db";
import {
  quotation,
  quotationItem,
} from "@my-better-t-app/db/schema/house-iq";
import { eq, and, sql } from "drizzle-orm";
import { checkRulesForItem } from "../lib/rule-engine";

export const itemRouter = router({
  add: orgProtectedProcedure
    .input(
      z.object({
        quotationId: z.string(),
        category: z.string().min(1),
        itemName: z.string().min(1),
        wbsCode: z.string().optional(),
        unit: z.string().min(1),
        quantity: z.number().positive().default(1),
      }),
    )
    .mutation(async ({ ctx, input }) => {
      // Verify quotation belongs to this organization
      const q = await db.query.quotation.findFirst({
        where: and(
          eq(quotation.id, input.quotationId),
          eq(quotation.organizationId, ctx.organizationId),
        ),
      });
      if (!q) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Quotation not found",
        });
      }

      // Get next sort order
      const [maxResult] = await db
        .select({ maxSort: sql<number>`coalesce(max(${quotationItem.sortOrder}), -1)` })
        .from(quotationItem)
        .where(eq(quotationItem.quotationId, input.quotationId));

      const [newItem] = await db
        .insert(quotationItem)
        .values({
          quotationId: input.quotationId,
          category: input.category,
          itemName: input.itemName,
          wbsCode: input.wbsCode,
          unit: input.unit,
          quantity: input.quantity,
          sortOrder: (maxResult?.maxSort ?? -1) + 1,
        })
        .returning();

      // Check rules and return alerts
      const alerts = newItem
        ? await checkRulesForItem(newItem, input.quotationId, ctx.organizationId)
        : [];

      return { item: newItem!, alerts };
    }),

  update: orgProtectedProcedure
    .input(
      z.object({
        id: z.string(),
        quotationId: z.string(),
        category: z.string().min(1).optional(),
        itemName: z.string().min(1).optional(),
        wbsCode: z.string().optional(),
        unit: z.string().min(1).optional(),
        quantity: z.number().positive().optional(),
      }),
    )
    .mutation(async ({ ctx, input }) => {
      // Verify ownership
      const q = await db.query.quotation.findFirst({
        where: and(
          eq(quotation.id, input.quotationId),
          eq(quotation.organizationId, ctx.organizationId),
        ),
      });
      if (!q) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Quotation not found",
        });
      }

      const { id, quotationId, ...data } = input;
      const [updated] = await db
        .update(quotationItem)
        .set(data)
        .where(
          and(
            eq(quotationItem.id, id),
            eq(quotationItem.quotationId, quotationId),
          ),
        )
        .returning();

      if (!updated) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Item not found",
        });
      }

      // Re-check rules after update
      const alerts = await checkRulesForItem(
        updated,
        quotationId,
        ctx.organizationId,
      );

      return { item: updated, alerts };
    }),

  remove: orgProtectedProcedure
    .input(z.object({ id: z.string(), quotationId: z.string() }))
    .mutation(async ({ ctx, input }) => {
      // Verify ownership
      const q = await db.query.quotation.findFirst({
        where: and(
          eq(quotation.id, input.quotationId),
          eq(quotation.organizationId, ctx.organizationId),
        ),
      });
      if (!q) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Quotation not found",
        });
      }

      await db
        .delete(quotationItem)
        .where(eq(quotationItem.id, input.id));

      return { success: true };
    }),

  reorder: orgProtectedProcedure
    .input(
      z.object({
        quotationId: z.string(),
        itemIds: z.array(z.string()),
      }),
    )
    .mutation(async ({ ctx, input }) => {
      // Verify ownership
      const q = await db.query.quotation.findFirst({
        where: and(
          eq(quotation.id, input.quotationId),
          eq(quotation.organizationId, ctx.organizationId),
        ),
      });
      if (!q) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Quotation not found",
        });
      }

      // Update sort order for each item
      for (let i = 0; i < input.itemIds.length; i++) {
        const itemId = input.itemIds[i]!;
        await db
          .update(quotationItem)
          .set({ sortOrder: i })
          .where(
            and(
              eq(quotationItem.id, itemId),
              eq(quotationItem.quotationId, input.quotationId),
            ),
          );
      }

      return { success: true };
    }),
});
