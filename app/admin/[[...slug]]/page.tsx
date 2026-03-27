import { redirect } from "next/navigation";
import { PortalShell } from "@/components/portal-shell";
import { PortalContent } from "@/components/portal-content";
import { getServerSession } from "@/lib/session";

export default async function AdminPortalPage({ params }: { params: Promise<{ slug?: string[] }> }) {
  const session = await getServerSession();
  if (!session || session.role !== "admin") redirect("/auth/admin/login");
  const { slug } = await params;
  return <PortalShell role="admin" currentUser={session.fullName}><PortalContent role="admin" slug={(slug ?? []).join("/")} /></PortalShell>;
}
