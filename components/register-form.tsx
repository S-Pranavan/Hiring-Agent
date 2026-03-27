"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Input, TextArea } from "@/components/forms";

export function RegisterForm() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(formData: FormData) {
    setLoading(true);
    setError("");
    const response = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        first_name: String(formData.get("first_name") ?? ""),
        last_name: String(formData.get("last_name") ?? ""),
        email: String(formData.get("email") ?? ""),
        phone: String(formData.get("phone") ?? ""),
        password: String(formData.get("password") ?? ""),
        summary: String(formData.get("summary") ?? ""),
      }),
    });
    const payload = await response.json();
    setLoading(false);
    if (!response.ok) {
      setError(payload.detail ?? "Registration failed.");
      return;
    }
    router.push("/candidate");
    router.refresh();
  }

  return <form action={onSubmit} className="panel p-8"><div className="grid gap-4 sm:grid-cols-2"><Input name="first_name" placeholder="First name" required /><Input name="last_name" placeholder="Last name" required /></div><div className="mt-4 grid gap-4 sm:grid-cols-2"><Input name="email" type="email" placeholder="Email address" required /><Input name="phone" placeholder="Phone number" /></div><div className="mt-4"><Input name="password" type="password" placeholder="Create password" required /></div><div className="mt-4"><TextArea name="summary" placeholder="Short professional summary" /></div><button disabled={loading} className="mt-6 rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white disabled:opacity-70">{loading ? "Creating account..." : "Create account"}</button>{error ? <p className="mt-4 text-sm text-rose-600">{error}</p> : null}<p className="mt-4 text-sm text-muted">Already registered? <Link href="/auth/candidate/login" className="font-medium text-primary">Sign in</Link></p></form>;
}
