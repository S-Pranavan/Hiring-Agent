import { NextRequest, NextResponse } from "next/server";
import { BACKEND_BASE_URL } from "@/lib/api";

export async function GET(_request: NextRequest, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  const response = await fetch(`${BACKEND_BASE_URL}/jobs/${id}`, { cache: "no-store" });
  const payload = await response.json();
  return NextResponse.json(payload, { status: response.status });
}