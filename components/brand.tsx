import Link from "next/link";

export function Brand() {
  return (
    <Link href="/" className="flex items-center gap-3 font-semibold text-ink">
      <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-brand text-sm font-bold text-white shadow-glow">AI</span>
      <span>
        <span className="block text-sm text-muted">Hiring Agent</span>
        <span className="block text-base">Enterprise Portal</span>
      </span>
    </Link>
  );
}