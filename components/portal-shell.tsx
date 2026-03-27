"use client";

import Link from "next/link";
import { Bell, Menu, Search } from "lucide-react";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Brand } from "@/components/brand";
import { LogoutButton } from "@/components/logout-button";
import { portalNav, roleThemes } from "@/lib/data";
import { Role } from "@/lib/types";
import { cn } from "@/lib/utils";

export function PortalShell({ role, children, currentUser }: Readonly<{ role: Role; children: React.ReactNode; currentUser: string }>) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const nav = portalNav[role];
  const theme = roleThemes[role];

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="flex min-h-screen">
        <aside className={cn("fixed inset-y-0 left-0 z-40 w-72 border-r border-border bg-white px-5 py-6 shadow-soft transition md:static md:translate-x-0", open ? "translate-x-0" : "-translate-x-full")}>
          <div className="flex items-center justify-between md:block">
            <Brand />
            <button onClick={() => setOpen(false)} className="rounded-full p-2 md:hidden"><Menu className="h-5 w-5" /></button>
          </div>
          <div className="mt-8 rounded-3xl bg-brand p-5 text-white shadow-glow">
            <p className="text-sm text-white/75">{theme.title}</p>
            <p className="mt-2 text-sm leading-6 text-white/90">{theme.subtitle}</p>
          </div>
          <nav className="mt-8 space-y-2">
            {nav.map((item) => (
              <Link key={item.href} href={item.href as any} className={cn("block rounded-2xl px-4 py-3 text-sm font-medium transition", pathname === item.href ? "bg-slate-100 text-ink" : "text-muted hover:bg-slate-50 hover:text-ink")}>
                {item.label}
              </Link>
            ))}
          </nav>
        </aside>
        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-30 border-b border-border bg-white/85 backdrop-blur-xl">
            <div className="flex h-20 items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
              <div className="flex items-center gap-3">
                <button onClick={() => setOpen((value) => !value)} className="rounded-full border border-border p-2 md:hidden"><Menu className="h-5 w-5" /></button>
                <div className="hidden rounded-full border border-border px-4 py-2 text-sm text-muted sm:flex sm:items-center sm:gap-2"><Search className="h-4 w-4" />Search candidates, jobs, reports</div>
              </div>
              <div className="flex items-center gap-3">
                <button className="rounded-full border border-border p-2"><Bell className="h-5 w-5 text-muted" /></button>
                <div className="rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-ink">{currentUser}</div>
                <LogoutButton />
              </div>
            </div>
          </header>
          <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
