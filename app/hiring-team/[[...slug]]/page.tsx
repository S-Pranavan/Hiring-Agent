import { redirect } from "next/navigation";
import { PortalShell } from "@/components/portal-shell";
import { PortalContent } from "@/components/portal-content";
import { getServerSession } from "@/lib/session";

export default async function HiringPortalPage({ params }: { params: Promise<{ slug?: string[] }> }) {
  const session = await getServerSession();
  if (!session || session.role !== "hiring") redirect("/auth/hiring/login");
  const { slug } = await params;
  return <PortalShell role="hiring" currentUser={session.fullName}><PortalContent role="hiring" slug={(slug ?? []).join("/")} /></PortalShell>;
}
