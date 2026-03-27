"use client";

import { useState } from "react";

const actionMap = [
  { label: "Reject", value: "reject" },
  { label: "Shortlist", value: "shortlist" },
  { label: "Select", value: "select" },
  { label: "Physical interview", value: "physical-interview" },
  { label: "Direct join", value: "direct-hire" },
] as const;

export function DecisionActions({ candidateId, jobId }: { candidateId: number; jobId: string }) {
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState<string | null>(null);

  async function handleAction(action: string) {
    setLoading(action);
    setStatus("");

    const response = await fetch(`/api/admin/decisions/${action}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidate_id: candidateId, job_id: jobId }),
    });

    const payload = await response.json();
    setLoading(null);
    setStatus(response.ok ? payload.message ?? "Decision recorded." : payload.detail ?? "Decision failed.");
  }

  return (
    <div>
      <div className="flex flex-wrap gap-3">
        {actionMap.map((action) => (
          <button
            key={action.value}
            type="button"
            onClick={() => handleAction(action.value)}
            disabled={loading !== null}
            className="rounded-full bg-brand px-5 py-3 text-sm font-semibold text-white disabled:opacity-70"
          >
            {loading === action.value ? "Saving..." : action.label}
          </button>
        ))}
      </div>
      {status ? <p className="mt-3 text-sm text-primary">{status}</p> : null}
    </div>
  );
}
