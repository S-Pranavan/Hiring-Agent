"use client";

import { FormEvent, useRef, useState } from "react";
import { Input, Select, TextArea } from "@/components/forms";

export function ApplicationForm() {
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<string>("");
  const formRef = useRef<HTMLFormElement>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setStatus("");

    const formData = new FormData(event.currentTarget);
    formData.set("job_id", String(formData.get("role") ?? ""));

    const response = await fetch("/api/applications", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();
    setLoading(false);
    setStatus(response.ok ? `Application submitted. Candidate ID: ${result.candidate_id}` : (result.detail ?? "Submission failed."));
    if (response.ok) {
      formRef.current?.reset();
      setSelectedFile("");
    }
  }

  return (
    <form ref={formRef} className="panel p-6" onSubmit={handleSubmit}>
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
        <div className="rounded-[1.5rem] border border-dashed border-blue-200 bg-blue-50/50 p-4">
          <label className="block text-sm font-semibold text-ink">Upload CV</label>
          <p className="mt-1 text-sm text-muted">PDF or DOCX up to 10MB. The file is stored locally now and can move to S3 later.</p>
          <input
            name="cv_file"
            type="file"
            accept=".pdf,.doc,.docx"
            className="mt-4 block w-full text-sm text-slate-600 file:mr-4 file:rounded-full file:border-0 file:bg-brand file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white"
            onChange={(event) => setSelectedFile(event.target.files?.[0]?.name ?? "")}
          />
          {selectedFile ? <p className="mt-3 text-sm text-primary">Selected: {selectedFile}</p> : null}
        </div>
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
