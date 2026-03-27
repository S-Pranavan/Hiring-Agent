import { getServerSession } from "@/lib/session";

export async function getBackendAuthHeaders(extraHeaders?: HeadersInit) {
  const session = await getServerSession();
  const headers = new Headers(extraHeaders);
  if (session?.backendToken) {
    headers.set("Authorization", `Bearer ${session.backendToken}`);
  }
  return headers;
}
