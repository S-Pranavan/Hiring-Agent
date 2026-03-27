import { NextRequest, NextResponse } from "next/server";
import { BACKEND_BASE_URL } from "@/lib/api";
import { createSessionToken, sessionCookieName } from "@/lib/session";

export async function POST(request: NextRequest) {
  const body = await request.json();
  const response = await fetch(`${BACKEND_BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await response.json();
  if (!response.ok) {
    return NextResponse.json(payload, { status: response.status });
  }

  const token = createSessionToken({
    userId: payload.user.id,
    fullName: payload.user.full_name,
    email: payload.user.email,
    role: payload.user.role,
    candidateId: payload.user.candidate_id ?? null,
    backendToken: payload.access_token,
  });

  const nextResponse = NextResponse.json({ user: payload.user }, { status: 201 });
  nextResponse.cookies.set(sessionCookieName, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: false,
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });
  return nextResponse;
}
