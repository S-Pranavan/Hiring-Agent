"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Input } from "@/components/forms";

export function AuthCard({ title, text, footer, role }: { title: string; text: string; footer: React.ReactNode; role: "candidate" | "admin" | "hiring" }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(formData: FormData) {
    setLoading(true);
    setError("");
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: String(formData.get("email") ?? ""),
        password: String(formData.get("password") ?? ""),
        role,
      }),
    });
    const payload = await response.json();
    setLoading(false);
    if (!response.ok) {
      setError(payload.detail ?? "Login failed.");
      return;
    }
    router.push(role === "candidate" ? "/candidate" : role === "admin" ? "/admin" : "/hiring-team");
    router.refresh();
  }

  return <div className="grid gap-8 lg:grid-cols-[0.85fr_1.15fr]"><div className="rounded-[2rem] bg-brand p-8 text-white shadow-glow"><span className="inline-flex rounded-full border border-white/20 px-3 py-1 text-xs uppercase tracking-[0.2em] text-white/70">Secure access</span><h1 className="mt-5 text-3xl font-semibold">{title}</h1><p className="mt-4 max-w-md leading-7 text-white/80">{text}</p><div className="mt-8 space-y-3">{["Role-based access control", "Audit-ready workflows", "Candidate-safe experience"].map((item) => <div key={item} className="rounded-2xl bg-white/10 px-4 py-3 text-sm backdrop-blur">{item}</div>)}</div></div><div className="panel p-8"><form action={onSubmit} className="space-y-4"><Input name="email" type="email" placeholder="Work email" required /><Input name="password" type="password" placeholder="Password" required /><Input name="company_or_id" placeholder="Optional company or candidate ID" /><button disabled={loading} className="w-full rounded-full bg-brand px-5 py-3 text-sm font-semibold text-white disabled:opacity-70">{loading ? "Signing in..." : "Continue"}</button></form>{error ? <p className="mt-4 text-sm text-rose-600">{error}</p> : null}<div className="mt-4 text-sm text-muted">{footer}</div><div className="mt-6 text-sm text-muted"><a href="/auth/forgot-password" className="font-medium text-primary">Forgot password?</a></div></div></div>;
}
