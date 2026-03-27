import { NextRequest, NextResponse } from "next/server";
import { BACKEND_BASE_URL } from "@/lib/api";
import { getBackendAuthHeaders } from "@/lib/backend-auth";

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ candidateId: string }> }
) {
  const { candidateId } = await params;
  const formData = await request.formData();
  const headers = await getBackendAuthHeaders();
  const response = await fetch(`${BACKEND_BASE_URL}/interviews/candidate/${candidateId}/complete`, {
    method: "POST",
    headers,
    body: formData,
  });
  const payload = await response.json();
  return NextResponse.json(payload, { status: response.status });
}
