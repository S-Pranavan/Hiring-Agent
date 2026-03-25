import { Briefcase, Brain, ShieldAlert, Sparkles } from "lucide-react";
import { Job, Metric, Role, TimelineItem } from "@/lib/types";

export const publicNav = [
  { label: "Platform", href: "/about" },
  { label: "Jobs", href: "/jobs" },
  { label: "Contact", href: "/contact" }
];

export const jobs: Job[] = [
  {
    id: "ai-product-designer",
    title: "AI Product Designer",
    location: "Colombo, Sri Lanka",
    type: "Hybrid",
    department: "Product",
    experience: "4+ years",
    summary: "Design intuitive recruiting experiences for enterprise hiring teams and candidates.",
    description: ["Lead UX strategy for AI-assisted recruiting workflows.", "Translate complex scoring into confident decision experiences."],
    requirements: ["Portfolio with SaaS workflow design", "Design systems experience", "Research depth"],
    responsibilities: ["Own candidate and reviewer journeys", "Partner with engineering and ML stakeholders", "Ship polished enterprise interfaces"],
    skills: ["Figma", "Design Systems", "User Research", "Product Thinking"],
    salary: "$60k - $85k",
    status: "Active"
  },
  {
    id: "ml-recruiting-ops-lead",
    title: "ML Recruiting Ops Lead",
    location: "Remote",
    type: "Full-time",
    department: "Operations",
    experience: "6+ years",
    summary: "Operationalize AI screening, fraud monitoring, and interview quality assurance.",
    description: ["Coordinate AI assessment pipelines across multiple hiring programs.", "Maintain recruiter trust with transparent QA and exception handling."],
    requirements: ["Hiring operations leadership", "AI tooling familiarity", "Excellent analytics communication"],
    responsibilities: ["Monitor workflows", "Review fraud signals", "Align decisions with hiring teams"],
    skills: ["Analytics", "Recruiting Ops", "Stakeholder Management", "Process Design"],
    salary: "$70k - $95k",
    status: "Active"
  },
  {
    id: "senior-full-stack-engineer",
    title: "Senior Full-Stack Engineer",
    location: "Singapore",
    type: "Remote",
    department: "Engineering",
    experience: "5+ years",
    summary: "Build the next generation of AI-assisted hiring infrastructure and portal workflows.",
    description: ["Deliver reliable internal and candidate-facing experiences.", "Implement role-aware analytics, interview tooling, and decision workflows."],
    requirements: ["Strong React and TypeScript", "API design", "Performance mindset"],
    responsibilities: ["Build portal features", "Own APIs", "Collaborate with design and data teams"],
    skills: ["Next.js", "TypeScript", "Node.js", "UX Engineering"],
    salary: "$90k - $130k",
    status: "Active"
  }
];

export const landingStats: Metric[] = [
  { label: "Screening accuracy", value: "94.8%", delta: "+8.2% QoQ", tone: "brand" },
  { label: "Time to shortlist", value: "18 hrs", delta: "-61% faster", tone: "success" },
  { label: "Fraud alerts flagged", value: "312", delta: "Realtime", tone: "warn" },
  { label: "Candidate NPS", value: "72", delta: "+11 pts", tone: "brand" }
];

export const featureCards = [
  { title: "AI scoring with human oversight", text: "Combine CV match, soft skills, ego patterns, fraud alerts, and interview signals in a single review surface.", icon: Brain },
  { title: "Structured hiring workflows", text: "Move candidates from application to final decision with auditable steps, role-based actions, and shared notes.", icon: Briefcase },
  { title: "Fraud-aware interview evidence", text: "Review recordings, screenshots, behavior markers, and timeline events inside one premium evidence workspace.", icon: ShieldAlert },
  { title: "Candidate-first experience", text: "Offer transparent application tracking, elegant interview scheduling, and mobile-friendly submissions.", icon: Sparkles }
];

export const portalNav: Record<Role, { label: string; href: string }[]> = {
  candidate: [
    { label: "Dashboard", href: "/candidate" },
    { label: "Profile", href: "/candidate/profile" },
    { label: "Apply", href: "/candidate/apply" },
    { label: "Tracking", href: "/candidate/tracking" },
    { label: "Notifications", href: "/candidate/notifications" },
    { label: "Interviews", href: "/candidate/interviews" },
    { label: "AI Interview", href: "/candidate/ai-interview" }
  ],
  admin: [
    { label: "Dashboard", href: "/admin" },
    { label: "Jobs", href: "/admin/jobs" },
    { label: "Candidates", href: "/admin/candidates" },
    { label: "Candidate Review", href: "/admin/candidates/review" },
    { label: "Interviews", href: "/admin/interviews" },
    { label: "Evidence", href: "/admin/evidence" },
    { label: "Comms", href: "/admin/communications" },
    { label: "Reports", href: "/admin/reports" },
    { label: "Final Decisions", href: "/admin/decisions" },
    { label: "Settings", href: "/admin/settings" }
  ],
  hiring: [
    { label: "Dashboard", href: "/hiring-team" },
    { label: "Shortlisted", href: "/hiring-team/shortlisted" },
    { label: "Interview Review", href: "/hiring-team/interviews" },
    { label: "Compare", href: "/hiring-team/comparison" },
    { label: "Collaboration", href: "/hiring-team/collaboration" }
  ]
};

export const dashboardMetrics: Record<Role, Metric[]> = {
  candidate: [
    { label: "Applications", value: "12", delta: "3 active", tone: "brand" },
    { label: "Interview invites", value: "2", delta: "1 this week", tone: "success" },
    { label: "Profile strength", value: "89%", delta: "Strong", tone: "brand" },
    { label: "Response time", value: "< 24h", delta: "Average", tone: "success" }
  ],
  admin: [
    { label: "Open roles", value: "26", delta: "+4 this week", tone: "brand" },
    { label: "Applicants", value: "1,842", delta: "+18%", tone: "success" },
    { label: "Fraud alerts", value: "17", delta: "Needs review", tone: "warn" },
    { label: "Offer ready", value: "14", delta: "High priority", tone: "brand" }
  ],
  hiring: [
    { label: "Assigned roles", value: "7", delta: "2 urgent", tone: "brand" },
    { label: "Reviews pending", value: "23", delta: "Due today", tone: "warn" },
    { label: "Strong fit", value: "11", delta: "Top quartile", tone: "success" },
    { label: "Consensus ready", value: "6", delta: "Awaiting signoff", tone: "brand" }
  ]
};

export const applicationTimeline: TimelineItem[] = [
  { stage: "Application submitted", status: "Completed", date: "Mar 21", detail: "CV and portfolio received successfully." },
  { stage: "AI screening", status: "Completed", date: "Mar 22", detail: "Strong role fit, collaboration, and clarity signals." },
  { stage: "Hiring review", status: "In progress", date: "Mar 24", detail: "The hiring team is reviewing interview readiness." },
  { stage: "Interview scheduling", status: "Upcoming", date: "Mar 27", detail: "Slots will be shared once review completes." }
];

export const pipelineRows = [
  ["Aisha Fernando", "Senior Product Manager", "92%", "87%", "Low", "81%", "Low"],
  ["Dinesh Perera", "Senior Full-Stack Engineer", "89%", "83%", "Medium", "88%", "Low"],
  ["Meera Silva", "AI Product Designer", "95%", "91%", "Low", "90%", "Low"],
  ["Ravi Jayasekara", "Operations Lead", "84%", "79%", "High", "76%", "Medium"]
];

export const comparisonRows = [
  { name: "Meera Silva", fit: "95%", interview: "90%", soft: "91%", fraud: "Low", note: "Balanced product thinking and communication." },
  { name: "Aisha Fernando", fit: "92%", interview: "88%", soft: "87%", fraud: "Low", note: "Strong leadership signals and stakeholder clarity." },
  { name: "Dinesh Perera", fit: "89%", interview: "88%", soft: "83%", fraud: "Low", note: "Excellent technical depth, moderate collaboration risk." }
];

export const trustIndicators = ["ISO-aligned review workflows", "Explainable AI scorecards", "Role-based audit visibility", "Mobile-ready candidate journeys"];
export const workflowSteps = [
  { title: "Capture", text: "Collect CVs, metadata, and portfolio inputs through elegant candidate workflows." },
  { title: "Analyze", text: "Score role fit, behavior signals, fraud indicators, and interview responses with explainable models." },
  { title: "Collaborate", text: "Give admins and hiring panels a shared workspace for evidence, notes, and decisions." },
  { title: "Decide", text: "Move candidates through shortlist, physical interview, select, or direct join actions." }
];
export const activityFeed = [
  "AI interview for Senior Full-Stack Engineer completed 12 minutes ago.",
  "Fraud evidence package generated for candidate Ravi Jayasekara.",
  "Physical interview invitation sent for AI Product Designer shortlist.",
  "Hiring team consensus updated for Senior Product Manager role."
];
export const reviewers = [
  { name: "Priya N.", role: "Engineering Manager", status: "Recommended", note: "Strong systems thinking." },
  { name: "Malik T.", role: "Head of Product", status: "Needs discussion", note: "Wants deeper leadership examples." },
  { name: "Sara L.", role: "Recruiting Lead", status: "Recommended", note: "High candidate quality and responsiveness." }
];
export const roleThemes: Record<Role, { title: string; subtitle: string }> = {
  candidate: { title: "Candidate Portal", subtitle: "Track progress, upload materials, and complete interviews with confidence." },
  admin: { title: "Admin Portal", subtitle: "Orchestrate hiring workflows, analytics, evidence reviews, and final decisions." },
  hiring: { title: "Hiring Team Portal", subtitle: "Review AI insights, compare candidates, and collaborate on final recommendations." }
};
export const quickActions = [
  { title: "Create job opening", detail: "Start a new req with AI-ready scoring criteria." },
  { title: "Invite shortlisted candidates", detail: "Send interviews or physical invites in one flow." },
  { title: "Review fraud queue", detail: "Inspect alerts, screenshots, and behavior markers." }
];
export const aboutVision = [
  { title: "Transparent AI", text: "Every recommendation is paired with evidence, context, and human review checkpoints." },
  { title: "Respectful candidate journeys", text: "We design every application and interview touchpoint to feel clear, mobile-friendly, and fair." },
  { title: "Operational confidence", text: "Teams get a decision-ready portal that reduces noise while preserving hiring judgment." }
];
export const supportCards = [
  { title: "Sales & partnerships", body: "Talk to the team about pilots, enterprise procurement, and implementation planning.", contact: "sales@aihireagent.com" },
  { title: "Candidate support", body: "Get help with applications, interview steps, accessibility needs, and account access.", contact: "support@aihireagent.com" },
  { title: "Security desk", body: "Reach out for security reviews, compliance requests, or incident reporting.", contact: "security@aihireagent.com" }
];