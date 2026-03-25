"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu } from "lucide-react";
import { useState } from "react";
import { Brand } from "@/components/brand";
import { publicNav } from "@/lib/data";
import { cn } from "@/lib/utils";

export function SiteHeader() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-white/90 backdrop-blur-xl">
      <div className="container-shell flex h-20 items-center justify-between gap-4">
        <Brand />
        <nav className="hidden items-center gap-2 md:flex">
          {publicNav.map((item) => (
            <Link key={item.href} href={item.href as any} className={cn("rounded-full px-4 py-2 text-sm font-medium transition hover:bg-slate-100", pathname === item.href ? "bg-slate-100 text-ink" : "text-muted") }>
              {item.label}
            </Link>
          ))}
          <Link href="/auth/candidate/register" className="rounded-full bg-brand px-5 py-3 text-sm font-semibold text-white">Get started</Link>
        </nav>
        <button className="rounded-full border border-border p-2 md:hidden" onClick={() => setOpen((value) => !value)}>
          <Menu className="h-5 w-5" />
        </button>
      </div>
      {open ? (
        <div className="border-t border-border bg-white md:hidden">
          <div className="container-shell flex flex-col gap-3 py-4">
            {publicNav.map((item) => (
              <Link key={item.href} href={item.href as any} className="rounded-2xl px-3 py-2 text-sm font-medium text-ink">
                {item.label}
              </Link>
            ))}
            <Link href="/auth/candidate/register" className="rounded-2xl bg-brand px-4 py-3 text-sm font-semibold text-white">Get started</Link>
          </div>
        </div>
      ) : null}
    </header>
  );
}