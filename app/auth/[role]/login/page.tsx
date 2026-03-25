import Link from "next/link";
import { AuthCard } from "@/components/auth-card";
import { SiteHeader } from "@/components/site-header";

const roleCopy = {
  candidate: "Sign in to manage applications, interview schedules, and progress tracking.",
  admin: "Sign in to manage jobs, analytics, communication flows, and final decisions.",
  hiring: "Sign in to review shortlists, interviews, and shared recommendations."
} as const;

export default async function LoginPage({ params }: { params: Promise<{ role: "candidate" | "admin" | "hiring" }> }) {
  const { role } = await params;
  return <div className="min-h-screen bg-surface"><SiteHeader /><main className="container-shell py-14"><AuthCard title={`${role === "hiring" ? "Hiring team" : role} login`} text={roleCopy[role]} footer={<>Need an account? <Link href="/auth/candidate/register" className="font-medium text-primary">Candidate registration</Link></>} /></main></div>;
}