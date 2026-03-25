import { cn } from "@/lib/utils";

export function Input({ className = "", ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input className={cn("w-full rounded-2xl border border-border bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-primary", className)} {...props} />;
}

export function TextArea({ className = "", ...props }: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={cn("min-h-[130px] w-full rounded-2xl border border-border bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-primary", className)} {...props} />;
}

export function Select({ className = "", children, ...props }: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={cn("w-full rounded-2xl border border-border bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-primary", className)} {...props}>{children}</select>;
}