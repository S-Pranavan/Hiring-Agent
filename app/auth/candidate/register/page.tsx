import { redirect } from "next/navigation";
import { RegisterForm } from "@/components/register-form";
import { SiteHeader } from "@/components/site-header";
import { getServerSession } from "@/lib/session";

export default async function CandidateRegisterPage() {
  const session = await getServerSession();
  if (session) {
    redirect(session.role === "candidate" ? "/candidate" : session.role === "admin" ? "/admin" : "/hiring-team");
  }

  return <div className="min-h-screen bg-surface"><SiteHeader /><main className="container-shell py-14"><div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr]"><div className="rounded-[2rem] bg-brand p-8 text-white shadow-glow"><h1 className="text-3xl font-semibold">Create your candidate account</h1><p className="mt-4 leading-7 text-white/85">Register once to track applications, upload documents, complete AI interviews, and receive status updates.</p></div><RegisterForm /></div></main></div>;
}
