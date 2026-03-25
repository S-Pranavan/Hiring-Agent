import { PortalShell } from "@/components/portal-shell";
import { PortalContent } from "@/components/portal-content";

export default async function CandidatePortalPage({ params }: { params: Promise<{ slug?: string[] }> }) {
  const { slug } = await params;
  return <PortalShell role="candidate"><PortalContent role="candidate" slug={(slug ?? []).join("/")} /></PortalShell>;
}