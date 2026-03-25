import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="border-t border-border bg-surface">
      <div className="container-shell flex flex-col gap-6 py-10 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="font-semibold text-ink">AI Hiring Agent System</p>
          <p className="mt-2 max-w-xl text-sm text-muted">Premium recruiting operations, AI-assisted interviews, and explainable decision workflows for enterprise teams.</p>
        </div>
        <div className="flex flex-wrap gap-4 text-sm text-muted">
          <Link href="/about">About</Link>
          <Link href="/jobs">Jobs</Link>
          <Link href="/contact">Contact</Link>
          <Link href="/auth/admin/login">Admin</Link>
          <Link href="/auth/hiring/login">Hiring Team</Link>
        </div>
      </div>
    </footer>
  );
}