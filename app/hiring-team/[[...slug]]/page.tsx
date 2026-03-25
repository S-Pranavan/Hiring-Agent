import { PortalShell } from "@/components/portal-shell";
import { PortalContent } from "@/components/portal-content";

export default async function HiringPortalPage({ params }: { params: Promise<{ slug?: string[] }> }) {
  const { slug } = await params;
  return <PortalShell role="hiring"><PortalContent role="hiring" slug={(slug ?? []).join("/")} /></PortalShell>;
}