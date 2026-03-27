import { redirect } from "next/navigation";
import { PortalShell } from "@/components/portal-shell";
import { PortalContent } from "@/components/portal-content";
import { getServerSession } from "@/lib/session";

export default async function CandidatePortalPage({ params }: { params: Promise<{ slug?: string[] }> }) {
  const session = await getServerSession();
  if (!session || session.role !== "candidate") redirect("/auth/candidate/login");
  const { slug } = await params;
  return <PortalShell role="candidate" currentUser={session.fullName}><PortalContent role="candidate" slug={(slug ?? []).join("/")} /></PortalShell>;
}
