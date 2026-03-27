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
  cv_file_name?: string | null;
  cv_file_type?: string | null;
  cv_file_size?: number;
};

export type CandidateProfile = {
  candidate: {
    id: number;
    full_name: string;
    email: string;
    status: string;
    job_id: string;
  };
  structured_cv: {
    summary: string;
    skills: string[];
    highlights: string[];
    source_file?: string | null;
    raw_text?: string;
  };
  cv_matching: {
    matching_score: number;
    passed_threshold: boolean;
    matched_skills?: string[];
  } | null;
  soft_skills: {
    overall_score: number;
    communication_score: number;
    leadership_score: number;
    teamwork_score?: number;
    adaptability_score?: number;
  } | null;
  ego_text: {
    ego_level: string;
    ego_score: number;
    reasoning?: string;
  } | null;
  final_score: {
    composite_score: number;
    recommendation: string;
  } | null;
  agent_status: {
    screening: string;
    soft_skills: string;
    ego: string;
    scheduling: string;
    interview: string;
    video_analysis: string;
    answer_evaluation: string;
  };
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

export type InterviewQuestion = {
  order: number;
  text: string;
  question_type: string;
  expected_answer: string;
  guidance: string;
};

export type InterviewAnswer = {
  question_order: number;
  answer_text: string;
  answer_type: string;
  score: number;
  feedback: string;
};

export type InterviewEvidenceMarker = {
  label: string;
  detail: string;
  severity: string;
};

export type InterviewEvidence = {
  video_file_name: string;
  video_file_type: string;
  video_file_size: number;
  video_path: string;
  notes: string;
  uploaded_at: string;
  markers: InterviewEvidenceMarker[];
};

export type InterviewSession = {
  session_id: string;
  candidate_id: number;
  job_id: string;
  status: string;
  current_question: number;
  questions: InterviewQuestion[];
  answers: InterviewAnswer[];
  evaluation: {
    final_score: number;
    summary_feedback: string;
    recommendation: string;
  } | null;
  fraud_analysis: {
    fraud_score: number;
    risk_level: string;
    signals: string[];
  } | null;
  evidence?: InterviewEvidence | null;
};

export type DashboardSummary = {
  received: number;
  shortlisted: number;
  interviewed: number;
  selected: number;
  fraud_alerts: number;
};

export type CommunicationLog = {
  id: number;
  candidate_id: number | null;
  candidate_name: string;
  channel: string;
  direction: string;
  subject: string;
  body: string;
  status: string;
  provider: string;
  created_at: string;
  recipient: string;
  metadata: Record<string, string>;
};
