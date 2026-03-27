export const sessionCookieName = "ha_session";
export const sessionSecret = process.env.SESSION_SECRET ?? "local-dev-session-secret-change-me";
export const sessionTtlSeconds = 60 * 60 * 24 * 7;

export type SessionPayload = {
  userId: number;
  fullName: string;
  email: string;
  role: "candidate" | "admin" | "hiring";
  candidateId?: number | null;
  backendToken: string;
  exp: number;
};
