import { Input, TextArea } from "@/components/forms";
import { SectionHeading } from "@/components/section-heading";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { supportCards } from "@/lib/data";

export default function ContactPage() {
  return <div className="min-h-screen"><SiteHeader /><main className="container-shell py-14"><SectionHeading eyebrow="Contact" title="Reach the right team quickly" text="Use the contact form for demos, implementation questions, support issues, or security requests." /><div className="mt-10 grid gap-8 lg:grid-cols-[0.9fr_1.1fr]"><div className="space-y-4">{supportCards.map((card) => <div key={card.title} className="panel p-6"><h3 className="text-lg font-semibold text-ink">{card.title}</h3><p className="mt-3 text-sm leading-7 text-muted">{card.body}</p><p className="mt-3 text-sm font-semibold text-primary">{card.contact}</p></div>)}</div><form className="panel p-8"><div className="grid gap-4 sm:grid-cols-2"><Input placeholder="First name" /><Input placeholder="Last name" /></div><div className="mt-4 grid gap-4 sm:grid-cols-2"><Input placeholder="Email address" /><Input placeholder="Company" /></div><div className="mt-4"><Input placeholder="Subject" /></div><div className="mt-4"><TextArea placeholder="Tell us what you need help with" /></div><button className="mt-6 rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white">Send message</button></form></div></main><SiteFooter /></div>;
}