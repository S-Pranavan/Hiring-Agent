import { UploadCloud } from "lucide-react";

export function UploadZone() {
  return <div className="rounded-[2rem] border border-dashed border-blue-200 bg-blue-50/50 p-8 text-center"><div className="mx-auto flex h-16 w-16 items-center justify-center rounded-3xl bg-brand text-white shadow-panel"><UploadCloud className="h-7 w-7" /></div><h3 className="mt-5 text-lg font-semibold text-ink">Drag and drop your CV</h3><p className="mt-2 text-sm leading-6 text-muted">Upload PDF or DOCX files up to 10MB. We will extract structure, skills, and experience automatically.</p><button className="mt-5 rounded-full bg-brand px-5 py-3 text-sm font-semibold text-white">Choose file</button></div>;
}