import { router, orgProtectedProcedure } from "../index";
import { db } from "@my-better-t-app/db";
import { wbsTag } from "@my-better-t-app/db/schema/house-iq";
import { asc } from "drizzle-orm";

export const wbsRouter = router({
  /** List all WBS tags grouped by category */
  list: orgProtectedProcedure.query(async () => {
    return db.query.wbsTag.findMany({
      orderBy: [asc(wbsTag.category), asc(wbsTag.nameTw)],
    });
  }),
});
