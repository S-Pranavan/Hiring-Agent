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
