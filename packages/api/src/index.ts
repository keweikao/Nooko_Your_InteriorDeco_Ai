import { initTRPC, TRPCError } from "@trpc/server";
import { db } from "@my-better-t-app/db";
import { member } from "@my-better-t-app/db/schema/auth";
import { eq } from "drizzle-orm";
import type { Context } from "./context";

export const t = initTRPC.context<Context>().create();

export const router = t.router;

export const publicProcedure = t.procedure;

export const protectedProcedure = t.procedure.use(({ ctx, next }) => {
  if (!ctx.session) {
    throw new TRPCError({
      code: "UNAUTHORIZED",
      message: "Authentication required",
      cause: "No session",
    });
  }
  return next({
    ctx: {
      ...ctx,
      session: ctx.session,
    },
  });
});

/** Organization-scoped procedure: requires auth + active organization */
export const orgProtectedProcedure = protectedProcedure.use(
  async ({ ctx, next }) => {
    // Try to get active org from session (set via Better Auth org plugin)
    let organizationId = (ctx.session.session as Record<string, unknown>)
      .activeOrganizationId as string | undefined;

    if (!organizationId) {
      // Fallback: get user's first organization membership
      const membership = await db.query.member.findFirst({
        where: eq(member.userId, ctx.session.user.id),
      });
      if (!membership) {
        throw new TRPCError({
          code: "FORBIDDEN",
          message:
            "No organization found. Please create or join an organization.",
        });
      }
      organizationId = membership.organizationId;
    }

    return next({
      ctx: {
        ...ctx,
        organizationId,
      },
    });
  },
);
