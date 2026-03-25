import { PortalShell } from "@/components/portal-shell";
import { PortalContent } from "@/components/portal-content";

export default async function AdminPortalPage({ params }: { params: Promise<{ slug?: string[] }> }) {
  const { slug } = await params;
  return <PortalShell role="admin"><PortalContent role="admin" slug={(slug ?? []).join("/")} /></PortalShell>;
}