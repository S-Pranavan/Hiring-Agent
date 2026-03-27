import { NextRequest, NextResponse } from "next/server";
import { sessionCookieName, verifySessionTokenEdge } from "@/lib/session-edge";

const rolePrefixes = [
  { prefix: "/candidate", role: "candidate" },
  { prefix: "/admin", role: "admin" },
  { prefix: "/hiring-team", role: "hiring" },
] as const;

export async function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const token = request.cookies.get(sessionCookieName)?.value;
  const session = await verifySessionTokenEdge(token ?? null);

  const matchedRolePrefix = rolePrefixes.find((item) => pathname.startsWith(item.prefix));
  if (matchedRolePrefix) {
    if (!session) {
      const loginUrl = new URL(`/auth/${matchedRolePrefix.role}/login`, request.url);
      return NextResponse.redirect(loginUrl);
    }
    if (session.role !== matchedRolePrefix.role) {
      const target = session.role === "candidate" ? "/candidate" : session.role === "admin" ? "/admin" : "/hiring-team";
      return NextResponse.redirect(new URL(target, request.url));
    }
  }

  if (pathname.startsWith("/auth/") && session) {
    const target = session.role === "candidate" ? "/candidate" : session.role === "admin" ? "/admin" : "/hiring-team";
    return NextResponse.redirect(new URL(target, request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/candidate/:path*", "/admin/:path*", "/hiring-team/:path*", "/auth/:path*"],
};
