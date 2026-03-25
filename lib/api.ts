import { dashboardMetrics, jobs as fallbackJobs } from "@/lib/data";
import {
  Application,
  CandidateProfile,
  DashboardSummary,
  InterviewItem,
  Job,
  Metric,
  NotificationItem
} from "@/lib/types";

const BACKEND_BASE_URL = process.env.BACKEND_API_URL ?? "http://127.0.0.1:8000/api/v1";

async function backendFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BACKEND_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Backend request failed: ${path}`);
  }

  return response.json() as Promise<T>;
}

export async function fetchJobs(): Promise<Job[]> {
  try {
    const data = await backendFetch<{ jobs: Job[] }>("/jobs/");
    return data.jobs;
  } catch {
    return fallbackJobs;
  }
}

export async function fetchJob(id: string): Promise<Job | null> {
  try {
    const data = await backendFetch<{ job: Job }>(`/jobs/${id}`);
    return data.job;
  } catch {
    return fallbackJobs.find((job) => job.id === id) ?? null;
  }
}

export async function fetchMetrics(role: string): Promise<Metric[]> {
  try {
    const data = await backendFetch<{ role: string; metrics: Metric[] }>(`/dashboard/metrics?role=${role}`);
    return data.metrics;
  } catch {
    return dashboardMetrics[role as keyof typeof dashboardMetrics] ?? dashboardMetrics.candidate;
  }
}

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  try {
    return await backendFetch<DashboardSummary>("/dashboard/summary");
  } catch {
    return {
      received: 1,
      shortlisted: 1,
      interviewed: 1,
      selected: 0,
      fraud_alerts: 0
    };
  }
}

export async function fetchApplications(): Promise<Application[]> {
  try {
    const data = await backendFetch<{ applications: Application[] }>("/candidates/");
    return data.applications;
  } catch {
    return [];
  }
}

export async function fetchCandidateProfile(candidateId: number): Promise<CandidateProfile | null> {
  try {
    return await backendFetch<CandidateProfile>(`/candidates/${candidateId}/profile`);
  } catch {
    return null;
  }
}

export async function fetchCandidateNotifications(candidateId: number): Promise<NotificationItem[]> {
  try {
    const data = await backendFetch<{ items: NotificationItem[] }>(`/interviews/candidate/${candidateId}/notifications`);
    return data.items;
  } catch {
    return [];
  }
}

export async function fetchCandidateInterviews(candidateId: number): Promise<InterviewItem[]> {
  try {
    const data = await backendFetch<{ items: InterviewItem[] }>(`/interviews/candidate/${candidateId}`);
    return data.items;
  } catch {
    return [];
  }
}

export async function createApplication(payload: {
  full_name: string;
  email: string;
  phone?: string;
  role: string;
  job_id: string;
  linkedin_url?: string;
  cover_letter?: string;
}) {
  return backendFetch<{ message: string; candidate_id: number }>("/candidates/upload", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export { BACKEND_BASE_URL };