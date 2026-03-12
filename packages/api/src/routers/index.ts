import {
  protectedProcedure,
  publicProcedure,
  router,
} from "../index";
import { quotationRouter } from "./quotation";
import { itemRouter } from "./items";
import { rulesRouter } from "./rules";
import { wbsRouter } from "./wbs";

export const appRouter = router({
  healthCheck: publicProcedure.query(() => {
    return "OK";
  }),
  privateData: protectedProcedure.query(({ ctx }) => {
    return {
      message: "This is private",
      user: ctx.session.user,
    };
  }),
  quotation: quotationRouter,
  item: itemRouter,
  rules: rulesRouter,
  wbs: wbsRouter,
});
export type AppRouter = typeof appRouter;
