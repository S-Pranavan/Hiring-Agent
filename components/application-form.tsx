"use client";

import { FormEvent, useState } from "react";
import { Input, Select, TextArea } from "@/components/forms";

export function ApplicationForm() {
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setStatus("");

    const formData = new FormData(event.currentTarget);
    const payload = {
      full_name: String(formData.get("full_name") ?? ""),
      email: String(formData.get("email") ?? ""),
      phone: String(formData.get("phone") ?? ""),
      role: String(formData.get("role") ?? ""),
      job_id: String(formData.get("job_id") ?? formData.get("role") ?? ""),
      linkedin_url: String(formData.get("linkedin_url") ?? ""),
      cover_letter: String(formData.get("cover_letter") ?? "")
    };

    const response = await fetch("/api/applications", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const result = await response.json();
    setLoading(false);
    setStatus(response.ok ? `Application submitted. Candidate ID: ${result.candidate_id}` : "Submission failed.");
    if (response.ok) {
      event.currentTarget.reset();
    }
  }

  return (
    <form className="panel p-6" onSubmit={handleSubmit}>
      <div className="grid gap-4 sm:grid-cols-2">
        <Input name="full_name" placeholder="Full name" required />
        <Input name="email" placeholder="Email address" required />
        <Input name="phone" placeholder="Phone number" required />
        <Select name="role" defaultValue="" required>
          <option value="" disabled>Select role</option>
          <option value="ai-product-designer">AI Product Designer</option>
          <option value="senior-full-stack-engineer">Senior Full-Stack Engineer</option>
          <option value="ml-recruiting-ops-lead">ML Recruiting Ops Lead</option>
        </Select>
      </div>
      <div className="mt-4 grid gap-4">
        <Input name="linkedin_url" placeholder="LinkedIn or portfolio URL" />
        <TextArea name="cover_letter" placeholder="Optional cover letter" />
      </div>
      <button disabled={loading} className="mt-6 rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white disabled:opacity-70">
        {loading ? "Submitting..." : "Submit application"}
      </button>
      {status ? <p className="mt-4 text-sm text-primary">{status}</p> : null}
    </form>
  );
}