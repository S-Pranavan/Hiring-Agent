"use client";

import { FormEvent, useMemo, useState } from "react";
import { Camera, Mic, MessageSquareText, ShieldAlert, TimerReset, UploadCloud, Video } from "lucide-react";
import { InterviewSession } from "@/lib/types";

function statusTone(status: string) {
  if (status === "completed") return "bg-emerald-50 text-emerald-700";
  if (status === "blocked") return "bg-rose-50 text-rose-700";
  if (status === "in_progress") return "bg-amber-50 text-amber-700";
  if (status === "recording_uploaded") return "bg-violet-50 text-violet-700";
  return "bg-blue-50 text-primary";
}

function formatBytes(bytes: number | undefined) {
  if (!bytes) return "0 KB";
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

export function VideoInterviewPanel({
  candidateId,
  initialSession,
}: {
  candidateId?: number;
  initialSession?: InterviewSession | null;
}) {
  const [session, setSession] = useState<InterviewSession | null>(initialSession ?? null);
  const [answer, setAnswer] = useState("");
  const [recordingNotes, setRecordingNotes] = useState("");
  const [recordingFile, setRecordingFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadingRecording, setUploadingRecording] = useState(false);
  const [message, setMessage] = useState("");

  const currentQuestion = useMemo(() => {
    if (!session?.questions.length) return null;
    return session.questions.find((item) => item.order === session.current_question) ?? session.questions[0];
  }, [session]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!candidateId || !currentQuestion || !answer.trim()) return;

    setLoading(true);
    setMessage("");

    const response = await fetch(`/api/interviews/${candidateId}/answers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question_order: currentQuestion.order,
        answer_text: answer,
        answer_type: "text",
      }),
    });

    const payload = await response.json();
    setLoading(false);

    if (!response.ok) {
      setMessage(payload.detail ?? "Answer submission failed.");
      return;
    }

    setSession(payload.session);
    setAnswer("");
    setMessage(payload.session.status === "completed" ? "Interview completed successfully." : "Answer submitted.");
  }

  async function handleEvidenceUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!candidateId || !recordingFile) return;

    setUploadingRecording(true);
    setMessage("");
    const formData = new FormData();
    formData.append("video_file", recordingFile);
    formData.append("notes", recordingNotes);

    const response = await fetch(`/api/interviews/${candidateId}/complete`, {
      method: "POST",
      body: formData,
    });
    const payload = await response.json();
    setUploadingRecording(false);

    if (!response.ok) {
      setMessage(payload.detail ?? "Recording upload failed.");
      return;
    }

    setSession(payload.session);
    setRecordingFile(null);
    setRecordingNotes("");
    setMessage("Interview evidence uploaded successfully.");
  }

  if (!session) {
    return <div className="panel p-6 text-sm text-muted">Interview session data is not available yet.</div>;
  }

  if (session.status === "blocked") {
    return <div className="panel p-6 text-sm text-muted">This candidate does not currently have an active AI interview session.</div>;
  }

  const latestAnswer = session.answers.find((item) => item.question_order === currentQuestion?.order);

  return (
    <div className="grid gap-6 xl:grid-cols-[1.4fr_0.6fr]">
      <div className="panel overflow-hidden">
        <div className="aspect-video bg-[radial-gradient(circle_at_top,rgba(37,99,235,0.2),transparent_30%),linear-gradient(135deg,#0F172A_0%,#1E293B_100%)] p-6 text-white">
          <div className="flex h-full flex-col justify-between rounded-[1.5rem] border border-white/10 p-5">
            <div className="flex items-center justify-between gap-3">
              <span className={`rounded-full px-3 py-1 text-xs uppercase tracking-[0.2em] ${statusTone(session.status)}`}>
                {session.status.replace("_", " ")}
              </span>
              <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold">Session {session.session_id}</span>
            </div>
            <div className="mx-auto text-center">
              <Video className="mx-auto h-14 w-14 text-white/70" />
              <p className="mt-4 text-lg font-medium">Interactive interview workspace</p>
              <p className="mt-2 text-sm text-white/70">
                Backend session, scoring, and stored evidence artifacts are connected locally.
              </p>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-3">
              {[Camera, Mic, MessageSquareText, TimerReset].map((Icon, index) => (
                <button key={index} type="button" className="rounded-full border border-white/20 bg-white/10 p-3 backdrop-blur">
                  <Icon className="h-5 w-5" />
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="panel p-5">
          <div className="flex items-center justify-between gap-3">
            <p className="text-sm text-muted">
              Question {currentQuestion?.order ?? session.current_question} of {session.questions.length}
            </p>
            {session.fraud_analysis ? (
              <span className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                <ShieldAlert className="h-3.5 w-3.5" />
                Fraud risk {session.fraud_analysis.risk_level}
              </span>
            ) : null}
          </div>
          <h3 className="mt-3 text-lg font-semibold text-ink">{currentQuestion?.text ?? "Interview complete"}</h3>
          <p className="mt-4 text-sm leading-6 text-muted">{currentQuestion?.guidance ?? session.evaluation?.summary_feedback ?? "No further questions."}</p>
        </div>

        <div className="panel p-5">
          <p className="text-sm font-medium text-muted">Progress</p>
          <p className="mt-3 text-4xl font-semibold text-ink">{session.answers.length}/{session.questions.length}</p>
          <div className="mt-4 h-3 rounded-full bg-slate-100">
            <div className="metric-bar h-3 rounded-full" style={{ width: `${session.questions.length ? (session.answers.length / session.questions.length) * 100 : 0}%` }} />
          </div>
          {session.evaluation ? (
            <div className="mt-4 rounded-2xl bg-slate-50 p-4 text-sm text-muted">
              <p className="font-semibold text-ink">Final score: {Math.round(session.evaluation.final_score)}%</p>
              <p className="mt-2">{session.evaluation.summary_feedback}</p>
              <p className="mt-2">Recommendation: {session.evaluation.recommendation}</p>
            </div>
          ) : (
            <form className="mt-4 space-y-3" onSubmit={handleSubmit}>
              <textarea
                value={answer}
                onChange={(event) => setAnswer(event.target.value)}
                placeholder="Type your answer here."
                className="min-h-32 w-full rounded-[1.5rem] border border-border bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/15"
              />
              <button disabled={loading || !currentQuestion} className="w-full rounded-full bg-brand px-5 py-3 text-sm font-semibold text-white disabled:opacity-70">
                {loading ? "Submitting..." : "Submit answer"}
              </button>
            </form>
          )}
          {latestAnswer ? (
            <div className="mt-4 rounded-2xl border border-border p-4 text-sm text-muted">
              <p className="font-semibold text-ink">Latest answer score: {Math.round(latestAnswer.score)}%</p>
              <p className="mt-2">{latestAnswer.feedback}</p>
            </div>
          ) : null}
        </div>

        <div className="panel p-5">
          <div className="flex items-center gap-2 text-sm font-medium text-muted">
            <UploadCloud className="h-4 w-4" />
            Interview Recording & Evidence
          </div>
          {session.evidence ? (
            <div className="mt-4 space-y-3 rounded-2xl bg-slate-50 p-4 text-sm text-muted">
              <p className="font-semibold text-ink">{session.evidence.video_file_name}</p>
              <p>Size: {formatBytes(session.evidence.video_file_size)}</p>
              <p>Uploaded: {new Date(session.evidence.uploaded_at).toLocaleString()}</p>
              {session.evidence.notes ? <p>Notes: {session.evidence.notes}</p> : null}
              <div className="space-y-2">
                {session.evidence.markers.map((marker) => (
                  <div key={`${marker.label}-${marker.detail}`} className="rounded-2xl border border-border bg-white px-3 py-2">
                    <p className="font-semibold text-ink">{marker.label}</p>
                    <p className="mt-1 text-xs text-muted">{marker.detail}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
          <form className="mt-4 space-y-3" onSubmit={handleEvidenceUpload}>
            <input
              type="file"
              accept=".webm,.mp4,.mov"
              className="block w-full text-sm text-slate-600 file:mr-4 file:rounded-full file:border-0 file:bg-brand file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white"
              onChange={(event) => setRecordingFile(event.target.files?.[0] ?? null)}
            />
            <textarea
              value={recordingNotes}
              onChange={(event) => setRecordingNotes(event.target.value)}
              placeholder="Add optional recording notes or context for reviewers."
              className="min-h-24 w-full rounded-[1.5rem] border border-border bg-white px-4 py-3 text-sm text-ink outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/15"
            />
            <button disabled={uploadingRecording || !recordingFile} className="w-full rounded-full bg-brand px-5 py-3 text-sm font-semibold text-white disabled:opacity-70">
              {uploadingRecording ? "Uploading evidence..." : "Upload interview recording"}
            </button>
          </form>
          {message ? <p className="mt-4 text-sm text-primary">{message}</p> : null}
        </div>
      </div>
    </div>
  );
}
