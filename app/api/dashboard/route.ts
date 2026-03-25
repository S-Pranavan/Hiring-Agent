import { NextRequest, NextResponse } from "next/server";
import { BACKEND_BASE_URL } from "@/lib/api";
import { Role } from "@/lib/types";

export async function GET(request: NextRequest) {
  const role = (request.nextUrl.searchParams.get("role") ?? "candidate") as Role;
  const response = await fetch(`${BACKEND_BASE_URL}/dashboard/metrics?role=${role}`, { cache: "no-store" });
  const payload = await response.json();
  return NextResponse.json(payload, { status: response.status });
}