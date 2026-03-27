import { ApplicationForm } from "@/components/application-form";
import { ChartCard } from "@/components/chart-card";
import { CommunicationCenter } from "@/components/communication-center";
import { DataTable } from "@/components/data-table";
import { DecisionActions } from "@/components/decision-actions";
import { Input, Select, TextArea } from "@/components/forms";
import { PortalPage } from "@/components/portal-page";
import { Timeline } from "@/components/timeline";
import { UploadZone } from "@/components/upload-zone";
import { VideoInterviewPanel } from "@/components/video-interview-panel";
import { activityFeed, comparisonRows, quickActions, reviewers } from "@/lib/data";
import {
  fetchApplications,
  fetchCandidateInterviews,
  fetchCandidateNotifications,
  fetchCandidateProfile,
  fetchCommunications,
  fetchDashboardSummary,
  fetchInterviewSession,
  fetchJobs,
  fetchMetrics,
} from "@/lib/api";
import { Application, CandidateProfile, Role } from "@/lib/types";

function profileRows(profile: CandidateProfile | null) {
  return [
    ["Match score", profile?.cv_matching ? `${profile.cv_matching.matching_score}%` : "Pending"],
    ["Soft skills", profile?.soft_skills ? `${profile.soft_skills.overall_score}%` : "Pending"],
    ["Ego analysis", profile?.ego_text ? profile.ego_text.ego_level : "Pending"],
    ["Final score", profile?.final_score ? `${profile.final_score.composite_score}%` : "Pending"],
    ["Recommendation", profile?.final_score?.recommendation ?? "Pending"],
  ];
}

function getPrimaryApplication(applications: Application[]) {
  return [...applications].sort((a, b) => b.id - a.id)[0] ?? null;
}

async function candidateContent(slug: string) {
  const applications = await fetchApplications();
  const primaryApplication = getPrimaryApplication(applications);
  const candidateId = primaryApplication?.id ?? 1;
  const [jobs, profile, notifications, interviews, session] = await Promise.all([
    fetchJobs(),
    fetchCandidateProfile(candidateId),
    fetchCandidateNotifications(candidateId),
    fetchCandidateInterviews(candidateId),
    fetchInterviewSession(candidateId),
  ]);

  switch (slug) {
    case "profile":
      return {
        title: "Profile",
        description: "Maintain your details, experience, skills, and resume.",
        body: (
          <section className="grid gap-6 xl:grid-cols-2">
            <div className="panel p-6">
              <h2 className="text-xl font-semibold text-ink">Personal information</h2>
              <div className="mt-5 grid gap-4 sm:grid-cols-2">
                <Input defaultValue={profile?.candidate.full_name.split(" ")[0] ?? "Ava"} />
                <Input defaultValue={profile?.candidate.full_name.split(" ").slice(1).join(" ") || "Morgan"} />
                <Input defaultValue={profile?.candidate.email ?? "ava@example.com"} />
                <Input defaultValue={primaryApplication?.phone ?? "+94 77 123 4567"} />
              </div>
              <h3 className="mt-8 text-lg font-semibold text-ink">AI summary</h3>
              <div className="mt-4 space-y-3">
                {profileRows(profile).map(([label, value]) => (
                  <div key={label} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
                    <span className="font-semibold text-ink">{label}:</span> {value}
                  </div>
                ))}
                {profile?.structured_cv.source_file ? (
                  <div className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
                    <span className="font-semibold text-ink">Uploaded CV:</span> {profile.structured_cv.source_file}
                  </div>
                ) : null}
              </div>
            </div>
            <div className="panel p-6">
              <h2 className="text-xl font-semibold text-ink">Experience summary</h2>
              <div className="mt-5 space-y-4">
                <TextArea defaultValue={profile?.structured_cv.summary ?? "Product leader with experience designing enterprise SaaS workflows and cross-functional operating models."} />
                <TextArea defaultValue={profile?.structured_cv.highlights.join("\n") || `Active application: ${primaryApplication?.role ?? "AI Product Designer"}. Status: ${primaryApplication?.status ?? "Hiring review"}.`} />
                <button className="rounded-full bg-brand px-5 py-3 text-sm font-semibold text-white">Save profile</button>
              </div>
            </div>
          </section>
        ),
      };
    case "apply":
      return {
        title: "CV Upload & Application",
        description: "Upload your resume, select a role, and submit supporting materials.",
        body: <section className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]"><UploadZone /><ApplicationForm /></section>,
      };
    case "tracking":
      return {
        title: "Application Tracking",
        description: "Follow every stage of your application.",
        body: <section className="panel p-6">{primaryApplication ? <Timeline items={primaryApplication.timeline} /> : <p className="text-sm text-muted">No application timeline available yet.</p>}</section>,
      };
    case "notifications":
      return {
        title: "Notifications",
        description: "Stay updated on interviews, status changes, and selection notices.",
        body: (
          <section className="grid gap-4">
            {notifications.length ? notifications.map((item) => (
              <div key={`${item.tag}-${item.title}`} className="panel p-6">
                <h2 className="text-lg font-semibold text-ink">{item.title}</h2>
                <p className="mt-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">{item.tag}</p>
                <p className="mt-3 text-sm leading-7 text-muted">{item.body}</p>
              </div>
            )) : <div className="panel p-6 text-sm text-muted">No notifications yet.</div>}
          </section>
        ),
      };
    case "interviews":
      return {
        title: "Interview Schedule",
        description: "Review upcoming interviews and confirmation status.",
        body: <section className="grid gap-6 lg:grid-cols-3">{interviews.length ? interviews.map((item) => <div key={`${item.type}-${item.date}`} className="panel p-6"><p className="text-sm text-muted">{item.type}</p><p className="mt-3 text-xl font-semibold text-ink">{item.date}</p><p className="mt-2 text-sm text-muted">{item.mode}</p><span className="mt-4 inline-flex rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-primary">{item.status}</span></div>) : <div className="panel p-6 text-sm text-muted">No interviews scheduled.</div>}</section>,
      };
    case "ai-interview":
      return {
        title: "AI Interview",
        description: "Complete a distraction-free interview session.",
        body: <VideoInterviewPanel candidateId={candidateId} initialSession={session} />,
      };
    default:
      return {
        title: `Welcome back, ${profile?.candidate.full_name.split(" ")[0] ?? "Ava"}`,
        description: "Monitor applications, interviews, and profile readiness from one premium dashboard.",
        body: (
          <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
            <div className="panel p-6">
              <h2 className="text-xl font-semibold text-ink">Application progress</h2>
              <div className="mt-6">{primaryApplication ? <Timeline items={primaryApplication.timeline} /> : <p className="text-sm text-muted">No active applications yet.</p>}</div>
            </div>
            <div className="space-y-6">
              <ChartCard
                title="Profile readiness"
                subtitle="A strong profile improves job recommendations and screening accuracy."
                values={[
                  { label: "Match score", value: profile?.cv_matching?.matching_score ?? 0 },
                  { label: "Soft skills", value: profile?.soft_skills?.overall_score ?? 0 },
                  { label: "Final score", value: profile?.final_score?.composite_score ?? 0 },
                ]}
              />
              <div className="panel p-6">
                <h2 className="text-xl font-semibold text-ink">Recommended jobs</h2>
                <div className="mt-4 space-y-4">
                  {jobs.slice(0, 3).map((job) => (
                    <div key={job.id} className="rounded-2xl bg-slate-50 p-4">
                      <p className="font-semibold text-ink">{job.title}</p>
                      <p className="mt-2 text-sm text-muted">{job.summary}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>
        ),
      };
  }
}

async function adminContent(slug: string) {
  const [jobs, applications, summary] = await Promise.all([
    fetchJobs(),
    fetchApplications(),
    fetchDashboardSummary(),
  ]);
  const primaryApplication = getPrimaryApplication(applications);
  const [profile, communicationLogs] = await Promise.all([
    primaryApplication ? fetchCandidateProfile(primaryApplication.id) : Promise.resolve(null),
    fetchCommunications(),
  ]);

  switch (slug) {
    case "jobs":
      return {
        title: "Job Management",
        description: "Create, edit, archive, and manage openings.",
        body: <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]"><form className="panel p-6"><h2 className="text-xl font-semibold text-ink">Create or edit job</h2><div className="mt-5 grid gap-4 sm:grid-cols-2"><Input placeholder="Role title" /><Input placeholder="Department" /><Input placeholder="Location" /><Select defaultValue="Active"><option>Active</option><option>Inactive</option><option>Archived</option></Select></div><div className="mt-4"><TextArea placeholder="Job summary, requirements, and AI scoring criteria" /></div><button className="mt-6 rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white">Save job</button></form><DataTable headers={["Role", "Department", "Location", "Status"]} rows={jobs.map((job) => [job.title, job.department, job.location, job.status])} /></section>,
      };
    case "candidates":
      return {
        title: "Candidate Management",
        description: "Review candidate records with search, sorting, AI scores, and fraud awareness.",
        body: <section className="space-y-6"><div className="grid gap-4 rounded-[2rem] border border-border bg-white p-4 md:grid-cols-4"><Input placeholder="Search candidate" /><Select defaultValue="All statuses"><option>All statuses</option><option>Shortlisted</option><option>Interviewed</option><option>Rejected</option></Select><Select defaultValue="Sort by score"><option>Sort by score</option><option>Match score</option><option>Fraud risk</option></Select><button className="rounded-2xl bg-brand px-4 py-3 text-sm font-semibold text-white">Apply</button></div><DataTable headers={["Candidate", "Role", "Match", "Soft Skills", "Ego", "Interview", "Fraud"]} rows={applications.map((application) => [application.candidate, application.role, application.match_score, application.soft_skills, application.ego, application.interview_score, application.fraud_risk])} /></section>,
      };
    case "candidates/review":
      return {
        title: "Candidate Detail Review",
        description: "Inspect CV data, AI signals, interview evidence, and notes.",
        body: <section className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]"><div className="space-y-6"><div className="panel p-6"><h2 className="text-xl font-semibold text-ink">Candidate profile summary</h2><p className="mt-4 text-sm leading-7 text-muted">{profile?.candidate.full_name ?? "Candidate"} is under review for {primaryApplication?.role ?? "the selected role"}.</p></div><div className="panel p-6"><h2 className="text-xl font-semibold text-ink">AI score breakdown</h2><div className="mt-4 space-y-3 text-sm text-muted">{profileRows(profile).map(([label, value]) => <p key={label}>{label}: {value}</p>)}</div></div></div><div className="grid gap-6"><div className="panel p-6"><h2 className="text-xl font-semibold text-ink">Structured CV</h2><p className="mt-4 text-sm leading-7 text-muted">{profile?.structured_cv.summary ?? "Structured CV data is not available yet."}</p>{profile?.structured_cv.source_file ? <p className="mt-3 text-sm text-primary">Source file: {profile.structured_cv.source_file}</p> : null}<div className="mt-4 flex flex-wrap gap-2">{profile?.structured_cv.skills.map((skill) => <span key={skill} className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">{skill}</span>)}</div></div><div className="panel p-6"><h2 className="text-xl font-semibold text-ink">Interview responses & evidence</h2><p className="mt-4 text-sm leading-7 text-muted">Latest interview score: {primaryApplication?.interview_score ?? "Pending"}. Fraud risk: {primaryApplication?.fraud_risk ?? "Pending"}.</p></div><div className="flex flex-wrap gap-3"><DecisionActions candidateId={primaryApplication?.id ?? 1} jobId={primaryApplication?.job_id ?? "ai-product-designer"} /></div></div></section>,
      };
    case "interviews":
      return {
        title: "Interview Management",
        description: "Reschedule interviews, track completion, and confirm readiness.",
        body: <section className="grid gap-6 lg:grid-cols-3">{[["Today", `${summary.interviewed} interviewed`, `${summary.received} applications received`],["Shortlisted", `${summary.shortlisted}`, "Candidates awaiting next steps"],["Fraud alerts", `${summary.fraud_alerts}`, "Needs review"]].map(([title, value, note]) => <div key={title} className="panel p-6"><p className="text-sm text-muted">{title}</p><p className="mt-3 text-3xl font-semibold text-ink">{value}</p><p className="mt-2 text-sm text-muted">{note}</p></div>)}</section>,
      };
    case "evidence":
      return {
        title: "Recording & Evidence Review",
        description: "Review interview video, logs, fraud screenshots, and behavior markers.",
        body: <VideoInterviewPanel candidateId={primaryApplication?.id} initialSession={primaryApplication ? await fetchInterviewSession(primaryApplication.id) : null} />,
      };
    case "communications":
      return {
        title: "Communication Center",
        description: "Manage templates, message logs, and interview invitation flows.",
        body: <CommunicationCenter applications={applications} initialLogs={communicationLogs} />,
      };
    case "reports":
      return {
        title: "Reports & Analytics",
        description: "Analyze the hiring funnel, role performance, and interview completion trends.",
        body: <section className="grid gap-6 xl:grid-cols-2"><ChartCard title="Selection rate" subtitle="Selection efficiency by funnel stage." values={[{ label: "Received", value: summary.received }, { label: "Shortlisted", value: summary.shortlisted }, { label: "Selected", value: summary.selected }]} /><ChartCard title="Interview completion" subtitle="Current pipeline snapshot from the backend summary endpoint." values={[{ label: "Interviewed", value: summary.interviewed }, { label: "Fraud alerts", value: summary.fraud_alerts }, { label: "Applications", value: summary.received }]} /></section>,
      };
    case "decisions":
      return {
        title: "Final Decision",
        description: "Compare shortlisted candidates and set final outcomes.",
        body: <section className="grid gap-6">{applications.map((application) => <div key={application.id} className="panel p-6"><div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between"><div><h2 className="text-xl font-semibold text-ink">{application.candidate}</h2><p className="mt-2 text-sm text-muted">Role: {application.role}</p></div><div className="flex flex-wrap gap-4 text-sm text-muted"><span>Fit: {application.match_score}</span><span>Interview: {application.interview_score}</span><span>Soft skills: {application.soft_skills}</span><span>Fraud: {application.fraud_risk}</span></div></div><div className="mt-5 flex flex-wrap gap-3"><DecisionActions candidateId={application.id} jobId={application.job_id} /></div></div>)}</section>,
      };
    case "settings":
      return {
        title: "Settings",
        description: "Manage profile settings, preferences, notifications, and access.",
        body: <section className="grid gap-6 xl:grid-cols-2"><div className="panel p-6"><h2 className="text-xl font-semibold text-ink">Profile settings</h2><div className="mt-5 space-y-4"><Input defaultValue="Ava Morgan" /><Input defaultValue="ava@aihireagent.com" /></div></div><div className="panel p-6"><h2 className="text-xl font-semibold text-ink">System preferences</h2><div className="mt-5 space-y-4"><Select defaultValue="Email and in-app"><option>Email and in-app</option><option>In-app only</option><option>Email only</option></Select><Select defaultValue="White-first premium"><option>White-first premium</option><option>System default</option></Select></div></div></section>,
      };
    default:
      return {
        title: "Admin Dashboard",
        description: "Track jobs, candidates, interview completion, fraud alerts, and workflow health.",
        body: <section className="grid gap-6 xl:grid-cols-[1fr_0.9fr]"><div className="grid gap-6"><ChartCard title="Hiring funnel" subtitle="Track progression from application through final decision." values={[{ label: "Applied", value: summary.received }, { label: "Shortlisted", value: summary.shortlisted }, { label: "Interviewed", value: summary.interviewed }, { label: "Selected", value: summary.selected }]} /><div className="panel p-6"><h2 className="text-xl font-semibold text-ink">Quick actions</h2><div className="mt-4 grid gap-4 md:grid-cols-3">{quickActions.map((action) => <div key={action.title} className="rounded-2xl bg-slate-50 p-4"><p className="font-semibold text-ink">{action.title}</p><p className="mt-2 text-sm leading-6 text-muted">{action.detail}</p></div>)}</div></div></div><div className="panel p-6"><h2 className="text-xl font-semibold text-ink">Live activity</h2><div className="mt-4 space-y-4">{activityFeed.map((item) => <div key={item} className="rounded-2xl border border-border p-4 text-sm leading-6 text-muted">{item}</div>)}</div></div></section>,
      };
  }
}

function hiringContent(slug: string, applications: Application[]) {
  switch (slug) {
    case "shortlisted":
      return { title: "Shortlisted Candidates", description: "Review AI results and add recommendations for shortlisted applicants.", body: <DataTable headers={["Candidate", "Role", "Match", "Soft Skills", "Ego", "Interview", "Fraud"]} rows={applications.map((application) => [application.candidate, application.role, application.match_score, application.soft_skills, application.ego, application.interview_score, application.fraud_risk]).slice(0, 3)} /> };
    case "interviews":
      return { title: "Interview Review", description: "Watch recordings, inspect answers, and review AI-generated insights.", body: <VideoInterviewPanel candidateId={getPrimaryApplication(applications)?.id} initialSession={null} /> };
    case "comparison":
      return { title: "Candidate Comparison", description: "Compare shortlisted candidates side by side.", body: <section className="grid gap-6 xl:grid-cols-3">{comparisonRows.map((candidate) => <div key={candidate.name} className="panel p-6"><h2 className="text-xl font-semibold text-ink">{candidate.name}</h2><div className="mt-5 space-y-3 text-sm text-muted"><p>Role fit: {candidate.fit}</p><p>Interview: {candidate.interview}</p><p>Soft skills: {candidate.soft}</p><p>Fraud: {candidate.fraud}</p></div><p className="mt-4 text-sm leading-6 text-muted">{candidate.note}</p></div>)}</section> };
    case "collaboration":
      return { title: "Decision Collaboration", description: "Share reviewer notes and move candidates toward final review.", body: <section className="grid gap-6 lg:grid-cols-3">{reviewers.map((reviewer) => <div key={reviewer.name} className="panel p-6"><h2 className="text-lg font-semibold text-ink">{reviewer.name}</h2><p className="mt-2 text-sm text-muted">{reviewer.role}</p><p className="mt-4 text-sm leading-6 text-muted">{reviewer.note}</p><span className="mt-4 inline-flex rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-primary">{reviewer.status}</span></div>)}</section> };
    default:
      return { title: "Hiring Dashboard", description: "Access assigned roles, shortlisted candidates, and review tasks.", body: <section className="grid gap-6 xl:grid-cols-[1fr_0.9fr]"><ChartCard title="Assigned role load" subtitle="Current review capacity across your queue." values={[{ label: "Candidate queue", value: applications.length || 0 }, { label: "Shortlisted", value: applications.filter((item) => item.status.toLowerCase().includes("hiring") || item.status.toLowerCase().includes("short") || item.status.toLowerCase().includes("scheduled")).length }, { label: "Review ready", value: applications.filter((item) => item.match_score !== "Pending").length }]} /><div className="panel p-6"><h2 className="text-xl font-semibold text-ink">Reviewer pulse</h2><div className="mt-4 space-y-4">{reviewers.map((reviewer) => <div key={reviewer.name} className="rounded-2xl border border-border p-4"><p className="font-semibold text-ink">{reviewer.name}</p><p className="mt-1 text-sm text-muted">{reviewer.role}</p><p className="mt-2 text-sm text-primary">{reviewer.status}</p></div>)}</div></div></section> };
  }
}

export async function PortalContent({ role, slug }: { role: Role; slug: string }) {
  const metrics = await fetchMetrics(role);
  const applications = await fetchApplications();
  const content = role === "candidate" ? await candidateContent(slug) : role === "admin" ? await adminContent(slug) : hiringContent(slug, applications);
  return <PortalPage role={role} title={content.title} description={content.description} metrics={metrics}>{content.body}</PortalPage>;
}
