import { NextResponse } from "next/server";
import { BACKEND_BASE_URL } from "@/lib/api";

export async function GET() {
  const response = await fetch(`${BACKEND_BASE_URL}/jobs/`, { cache: "no-store" });
  const payload = await response.json();
  return NextResponse.json(payload, { status: response.status });
}