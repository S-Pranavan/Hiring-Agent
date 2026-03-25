import { LucideIcon } from "lucide-react";

export function FeatureCard({ icon: Icon, title, text }: { icon: LucideIcon; title: string; text: string }) {
  return (
    <div className="tilt-card panel p-6">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand text-white shadow-glow">
        <Icon className="h-6 w-6" />
      </div>
      <h3 className="mt-6 text-xl font-semibold text-ink">{title}</h3>
      <p className="mt-3 leading-7 text-muted">{text}</p>
    </div>
  );
}