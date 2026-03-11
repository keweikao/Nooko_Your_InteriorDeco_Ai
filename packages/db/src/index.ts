import { env } from "@my-better-t-app/env/server";
import * as schema from "./schema";

import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';

const sql = neon(env.DATABASE_URL);
export const db = drizzle(sql, { schema });

