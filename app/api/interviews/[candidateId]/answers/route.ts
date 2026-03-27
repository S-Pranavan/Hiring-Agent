import { NextRequest, NextResponse } from "next/server";
import { BACKEND_BASE_URL } from "@/lib/api";
import { getBackendAuthHeaders } from "@/lib/backend-auth";

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ candidateId: string }> }
) {
  const { candidateId } = await params;
  const body = await request.json();
  const headers = await getBackendAuthHeaders({ "Content-Type": "application/json" });
  const response = await fetch(`${BACKEND_BASE_URL}/interviews/candidate/${candidateId}/answers`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  const payload = await response.json();
  return NextResponse.json(payload, { status: response.status });
}
