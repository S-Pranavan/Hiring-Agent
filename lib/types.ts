export type Role = "candidate" | "admin" | "hiring";

export type Job = {
  id: string;
  title: string;
  location: string;
  type: string;
  department: string;
  experience: string;
  summary: string;
  description: string[];
  requirements: string[];
  responsibilities: string[];
  skills: string[];
  salary: string;
  status: "Active" | "Archived";
};

export type Metric = {
  label: string;
  value: string;
  delta?: string;
  tone?: "brand" | "success" | "warn" | "danger";
};

export type TimelineItem = {
  stage: string;
  status: string;
  date: string;
  detail: string;
};

export type Application = {
  id: number;
  candidate: string;
  email: string;
  phone: string;
  role: string;
  job_id: string;
  status: string;
  match_score: string;
  soft_skills: string;
  ego: string;
  interview_score: string;
  fraud_risk: string;
  timeline: TimelineItem[];
};

export type CandidateProfile = {
  candidate: {
    id: number;
    full_name: string;
    email: string;
    status: string;
    job_id: string;
  };
  cv_matching: {
    matching_score: number;
    passed_threshold: boolean;
  } | null;
  soft_skills: {
    overall_score: number;
    communication_score: number;
    leadership_score: number;
  } | null;
  ego_text: {
    ego_level: string;
    ego_score: number;
  } | null;
  final_score: {
    composite_score: number;
    recommendation: string;
  } | null;
};

export type NotificationItem = {
  title: string;
  body: string;
  tag: string;
};

export type InterviewItem = {
  type: string;
  date: string;
  mode: string;
  status: string;
};

export type DashboardSummary = {
  received: number;
  shortlisted: number;
  interviewed: number;
  selected: number;
  fraud_alerts: number;
};