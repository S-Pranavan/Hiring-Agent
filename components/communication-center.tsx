"use client";

import { useMemo, useState } from "react";

import { Application, CommunicationLog } from "@/lib/types";

const templateOptions = [
  { value: "status_update", label: "Status update" },
  { value: "selection", label: "Selection email" },
  { value: "rejection", label: "Rejection email" },
  { value: "physical_interview", label: "Physical interview invite" },
] as const;

const channelOptions = [
  { value: "email", label: "Email" },
  { value: "call", label: "Voice call" },
] as const;

function formatTimestamp(value: string) {
  if (!value) {
    return "Just now";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

export function CommunicationCenter({
  applications,
  initialLogs,
}: {
  applications: Application[];
  initialLogs: CommunicationLog[];
}) {
  const [selectedCandidateId, setSelectedCandidateId] = useState<number>(applications[0]?.id ?? 0);
  const [template, setTemplate] = useState<string>("status_update");
  const [channel, setChannel] = useState<string>("email");
  const [customMessage, setCustomMessage] = useState("");
  const [logs, setLogs] = useState<CommunicationLog[]>(initialLogs);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const selectedCandidate = useMemo(
    () => applications.find((application) => application.id === selectedCandidateId) ?? applications[0] ?? null,
    [applications, selectedCandidateId],
  );

  async function refreshLogs() {
    const response = await fetch("/api/admin/communications", { cache: "no-store" });
    const payload = await response.json();
    if (response.ok) {
      setLogs(payload.items ?? []);
    }
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCandidate) {
      setStatus("No candidate is available for communication.");
      return;
    }

    setLoading(true);
    setStatus("");

    const response = await fetch("/api/admin/communications", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        candidate_id: selectedCandidate.id,
        template,
        channel,
        custom_message: customMessage,
      }),
    });

    const payload = await response.json();
    setLoading(false);

    if (!response.ok) {
      setStatus(payload.detail ?? "Communication failed.");
      return;
    }

    setStatus(`${payload.message} ${payload.delivery?.status ? `Delivery: ${payload.delivery.status}.` : ""}`.trim());
    setCustomMessage("");
    await refreshLogs();
  }

  return (
    <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
      <form onSubmit={handleSubmit} className="panel p-6">
        <h2 className="text-xl font-semibold text-ink">Trigger communication</h2>
        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          <label className="text-sm text-muted">
            Candidate
            <select
              value={selectedCandidateId}
              onChange={(event) => setSelectedCandidateId(Number(event.target.value))}
              className="mt-2 w-full rounded-2xl border border-border bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-primary"
            >
              {applications.map((application) => (
                <option key={application.id} value={application.id}>
                  {application.candidate} · {application.role}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm text-muted">
            Channel
            <select
              value={channel}
              onChange={(event) => setChannel(event.target.value)}
              className="mt-2 w-full rounded-2xl border border-border bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-primary"
            >
              {channelOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm text-muted sm:col-span-2">
            Template
            <select
              value={template}
              onChange={(event) => setTemplate(event.target.value)}
              className="mt-2 w-full rounded-2xl border border-border bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-primary"
            >
              {templateOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="mt-4 rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">
          <p className="font-semibold text-ink">{selectedCandidate?.candidate ?? "No candidate selected"}</p>
          <p className="mt-1">Email: {selectedCandidate?.email ?? "Unavailable"}</p>
          <p className="mt-1">Phone: {selectedCandidate?.phone || "Unavailable"}</p>
        </div>
        <label className="mt-4 block text-sm text-muted">
          Custom message
          <textarea
            value={customMessage}
            onChange={(event) => setCustomMessage(event.target.value)}
            placeholder="Optional custom message. Leave blank to use the selected template."
            className="mt-2 min-h-[150px] w-full rounded-2xl border border-border bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-primary"
          />
        </label>
        <button
          type="submit"
          disabled={loading || !applications.length}
          className="mt-6 rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white disabled:opacity-70"
        >
          {loading ? "Sending..." : "Send communication"}
        </button>
        {status ? <p className="mt-3 text-sm text-primary">{status}</p> : null}
      </form>

      <div className="panel p-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-ink">Sent message log</h2>
            <p className="mt-2 text-sm text-muted">Delivery status, provider, and latest outreach records.</p>
          </div>
          <button
            type="button"
            onClick={refreshLogs}
            className="rounded-full border border-border px-4 py-2 text-sm font-semibold text-ink"
          >
            Refresh
          </button>
        </div>
        <div className="mt-5 space-y-4">
          {logs.length ? (
            logs.map((item) => (
              <div key={item.id} className="rounded-3xl border border-border bg-slate-50/80 p-4 shadow-soft">
                <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <p className="font-semibold text-ink">{item.subject || "Communication event"}</p>
                    <p className="mt-1 text-sm text-muted">
                      {item.candidate_name} · {item.recipient || "Portal log"}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2 text-xs font-semibold uppercase tracking-[0.16em]">
                    <span className="rounded-full bg-white px-3 py-1 text-slate-600">{item.channel}</span>
                    <span className="rounded-full bg-white px-3 py-1 text-slate-600">{item.provider}</span>
                    <span className="rounded-full bg-blue-50 px-3 py-1 text-primary">{item.status}</span>
                  </div>
                </div>
                <p className="mt-3 text-sm leading-7 text-muted">{item.body}</p>
                <p className="mt-3 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  {formatTimestamp(item.created_at)}
                </p>
              </div>
            ))
          ) : (
            <div className="rounded-3xl border border-dashed border-border p-6 text-sm text-muted">
              No communication records yet.
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
