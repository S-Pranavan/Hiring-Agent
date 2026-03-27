import { NextResponse } from "next/server";
import { BACKEND_BASE_URL } from "@/lib/api";
import { getBackendAuthHeaders } from "@/lib/backend-auth";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ candidateId: string }> }
) {
  const { candidateId } = await params;
  const headers = await getBackendAuthHeaders();
  const response = await fetch(`${BACKEND_BASE_URL}/interviews/candidate/${candidateId}/session`, { cache: "no-store", headers });
  const payload = await response.json();
  return NextResponse.json(payload, { status: response.status });
}
