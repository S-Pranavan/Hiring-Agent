import { Metric } from "@/lib/types";
import { cn } from "@/lib/utils";

const toneMap = {
  brand: "bg-blue-50 text-primary",
  success: "bg-emerald-50 text-emerald-600",
  warn: "bg-amber-50 text-amber-600",
  danger: "bg-rose-50 text-rose-600"
};

export function MetricCard({ metric }: { metric: Metric }) {
  return (
    <div className="tilt-card panel-3d p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-muted">{metric.label}</p>
          <p className="mt-3 text-3xl font-semibold text-ink">{metric.value}</p>
        </div>
        {metric.delta ? <span className={cn("rounded-full px-3 py-1 text-xs font-semibold", toneMap[metric.tone ?? "brand"])}>{metric.delta}</span> : null}
      </div>
    </div>
  );
}