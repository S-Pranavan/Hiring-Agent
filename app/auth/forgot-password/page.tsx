import { Input } from "@/components/forms";
import { SiteHeader } from "@/components/site-header";

export default function ForgotPasswordPage() {
  return <div className="min-h-screen bg-surface"><SiteHeader /><main className="container-shell py-14"><div className="mx-auto max-w-2xl panel p-8"><h1 className="text-3xl font-semibold text-ink">Forgot password</h1><p className="mt-4 leading-7 text-muted">Enter your work or candidate email address and we will send a secure reset link.</p><div className="mt-6 space-y-4"><Input placeholder="Email address" /><button className="rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white">Send reset link</button></div></div></main></div>;
}