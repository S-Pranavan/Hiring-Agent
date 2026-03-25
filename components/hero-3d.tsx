"use client";

import { motion } from "framer-motion";
import { landingStats } from "@/lib/data";

export function Hero3D() {
  return (
    <div className="relative min-h-[520px] overflow-hidden rounded-[2rem] border border-white/70 bg-white shadow-soft">
      <div className="hero-orb left-10 top-10 h-24 w-24" />
      <div className="hero-orb bottom-16 right-16 h-32 w-32 opacity-70" />
      <div className="grid-fade absolute inset-0 opacity-70" />
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }} className="relative grid h-full gap-8 p-8 lg:grid-cols-[1.15fr_0.85fr] lg:p-10">
        <div className="flex flex-col justify-between gap-8">
          <div className="space-y-6">
            <div className="inline-flex rounded-full border border-blue-100 bg-blue-50 px-4 py-2 text-sm font-medium text-primary">AI-first recruiting intelligence</div>
            <div className="max-w-2xl">
              <h1 className="text-4xl font-semibold tracking-tight text-ink sm:text-5xl lg:text-6xl">Enterprise hiring with <span className="gradient-text">clarity, speed, and evidence</span>.</h1>
              <p className="mt-6 max-w-xl text-lg leading-8 text-muted">A premium portal for candidates, admins, and hiring teams to manage applications, interviews, AI scoring, and final decisions in one clean system.</p>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {landingStats.map((metric, index) => (
              <motion.div key={metric.label} initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.15 + index * 0.08 }} className="tilt-card rounded-3xl border border-white/60 bg-white/85 p-5 shadow-soft backdrop-blur">
                <p className="text-sm text-muted">{metric.label}</p>
                <p className="mt-3 text-3xl font-semibold text-ink">{metric.value}</p>
                <p className="mt-2 text-sm font-medium text-primary">{metric.delta}</p>
              </motion.div>
            ))}
          </div>
        </div>
        <div className="relative flex items-center justify-center">
          <div className="relative h-[360px] w-full max-w-[420px]">
            <motion.div animate={{ y: [0, -10, 0] }} transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }} className="absolute left-6 top-8 w-[78%] rounded-[2rem] border border-white/80 bg-white/85 p-5 shadow-soft backdrop-blur">
              <div className="flex items-center justify-between"><p className="text-sm font-semibold text-ink">AI Workflow Summary</p><span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-600">Stable</span></div>
              <div className="mt-5 space-y-4">{[["CV match score", "92%"],["Soft skills score", "89%"],["Fraud alert risk", "Low"],["Interview quality", "Excellent"]].map(([label, value]) => <div key={label} className="rounded-2xl bg-slate-50 p-4"><div className="flex items-center justify-between text-sm"><span className="text-muted">{label}</span><span className="font-semibold text-ink">{value}</span></div></div>)}</div>
            </motion.div>
            <motion.div animate={{ y: [0, 12, 0] }} transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }} className="absolute bottom-6 right-0 w-[72%] rounded-[2rem] bg-brand p-5 text-white shadow-glow">
              <p className="text-sm text-white/75">Decision Readiness</p>
              <p className="mt-3 text-4xl font-semibold">86%</p>
              <div className="mt-5 space-y-3">
                <div className="rounded-2xl bg-white/14 p-4 backdrop-blur"><p className="text-xs uppercase tracking-[0.2em] text-white/70">Collaboration</p><p className="mt-2 text-lg font-semibold">3 reviewers aligned</p></div>
                <div className="rounded-2xl bg-white/14 p-4 backdrop-blur"><p className="text-xs uppercase tracking-[0.2em] text-white/70">Next step</p><p className="mt-2 text-lg font-semibold">Physical interview</p></div>
              </div>
            </motion.div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}