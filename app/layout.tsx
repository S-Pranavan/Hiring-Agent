import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Hiring Agent System",
  description: "A premium enterprise portal for AI-assisted hiring workflows."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}