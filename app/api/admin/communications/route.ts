import { NextRequest, NextResponse } from "next/server";
import { BACKEND_BASE_URL } from "@/lib/api";
import { getBackendAuthHeaders } from "@/lib/backend-auth";

export async function GET() {
  const headers = await getBackendAuthHeaders();
  const response = await fetch(`${BACKEND_BASE_URL}/admin/communications`, {
    cache: "no-store",
    headers,
  });
  const payload = await response.json();
  return NextResponse.json(payload, { status: response.status });
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const headers = await getBackendAuthHeaders({ "Content-Type": "application/json" });
  const response = await fetch(`${BACKEND_BASE_URL}/admin/communications/send`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  const payload = await response.json();
  return NextResponse.json(payload, { status: response.status });
}
