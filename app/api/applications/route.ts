import { NextRequest, NextResponse } from "next/server";
import { BACKEND_BASE_URL } from "@/lib/api";

export async function GET() {
  const response = await fetch(`${BACKEND_BASE_URL}/candidates/`, { cache: "no-store" });
  const payload = await response.json();
  return NextResponse.json(payload, { status: response.status });
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const response = await fetch(`${BACKEND_BASE_URL}/candidates/upload`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  const payload = await response.json();
  return NextResponse.json(payload, { status: response.status });
}