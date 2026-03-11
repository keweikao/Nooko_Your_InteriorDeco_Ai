import { createAuthClient } from "better-auth/react";
import { env } from "@my-better-t-app/env/web";

export const authClient = createAuthClient({
	baseURL: env.VITE_SERVER_URL,
});
