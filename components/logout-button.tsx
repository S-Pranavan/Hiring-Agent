"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export function LogoutButton() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleLogout() {
    setLoading(true);
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/");
    router.refresh();
  }

  return <button onClick={handleLogout} disabled={loading} className="rounded-full border border-border px-4 py-2 text-sm font-medium text-ink disabled:opacity-70">{loading ? "Signing out..." : "Sign out"}</button>;
}
