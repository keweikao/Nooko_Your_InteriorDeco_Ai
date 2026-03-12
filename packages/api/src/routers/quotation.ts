import { z } from "zod";
import { TRPCError } from "@trpc/server";
import { router, orgProtectedProcedure } from "../index";
import { db } from "@my-better-t-app/db";
import { quotation } from "@my-better-t-app/db/schema/house-iq";
import { eq, and, desc } from "drizzle-orm";

export const quotationRouter = router({
  create: orgProtectedProcedure
    .input(
      z.object({
        projectName: z.string().min(1),
        projectAddress: z.string().optional(),
      }),
    )
    .mutation(async ({ ctx, input }) => {
      const [newQuotation] = await db
        .insert(quotation)
        .values({
          organizationId: ctx.organizationId,
          createdBy: ctx.session.user.id,
          projectName: input.projectName,
          projectAddress: input.projectAddress,
        })
        .returning();
      return newQuotation;
    }),

  list: orgProtectedProcedure.query(async ({ ctx }) => {
    return db.query.quotation.findMany({
      where: eq(quotation.organizationId, ctx.organizationId),
      orderBy: desc(quotation.createdAt),
      with: { createdByUser: true },
    });
  }),

  get: orgProtectedProcedure
    .input(z.object({ id: z.string() }))
    .query(async ({ ctx, input }) => {
      const result = await db.query.quotation.findFirst({
        where: and(
          eq(quotation.id, input.id),
          eq(quotation.organizationId, ctx.organizationId),
        ),
        with: {
          items: {
            orderBy: (items, { asc }) => [asc(items.sortOrder)],
          },
          createdByUser: true,
        },
      });
      if (!result) {
        throw new TRPCError({ code: "NOT_FOUND", message: "Quotation not found" });
      }
      return result;
    }),

  update: orgProtectedProcedure
    .input(
      z.object({
        id: z.string(),
        projectName: z.string().min(1).optional(),
        projectAddress: z.string().optional(),
        status: z.enum(["draft", "reviewing", "completed"]).optional(),
      }),
    )
    .mutation(async ({ ctx, input }) => {
      const { id, ...data } = input;
      const [updated] = await db
        .update(quotation)
        .set(data)
        .where(
          and(
            eq(quotation.id, id),
            eq(quotation.organizationId, ctx.organizationId),
          ),
        )
        .returning();
      if (!updated) {
        throw new TRPCError({ code: "NOT_FOUND", message: "Quotation not found" });
      }
      return updated;
    }),

  delete: orgProtectedProcedure
    .input(z.object({ id: z.string() }))
    .mutation(async ({ ctx, input }) => {
      const [deleted] = await db
        .delete(quotation)
        .where(
          and(
            eq(quotation.id, input.id),
            eq(quotation.organizationId, ctx.organizationId),
          ),
        )
        .returning();
      if (!deleted) {
        throw new TRPCError({ code: "NOT_FOUND", message: "Quotation not found" });
      }
      return { success: true };
    }),
});
