import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        surface: "#F8FAFC",
        ink: "#0F172A",
        muted: "#64748B",
        border: "#E2E8F0",
        primary: "#2563EB",
        secondary: "#7C3AED"
      },
      boxShadow: {
        soft: "0 20px 60px rgba(15, 23, 42, 0.08)",
        panel: "0 18px 40px rgba(37, 99, 235, 0.10)",
        glow: "0 10px 30px rgba(124, 58, 237, 0.18)"
      },
      borderRadius: {
        "4xl": "2rem"
      },
      backgroundImage: {
        brand: "linear-gradient(135deg, #2563EB 0%, #7C3AED 100%)",
        brandAlt: "linear-gradient(135deg, #4F46E5 0%, #8B5CF6 100%)",
        grid: "radial-gradient(circle at top, rgba(37,99,235,0.12), transparent 35%), linear-gradient(to right, rgba(148,163,184,0.1) 1px, transparent 1px), linear-gradient(to bottom, rgba(148,163,184,0.1) 1px, transparent 1px)"
      },
      fontFamily: {
        sans: ["ui-sans-serif", "system-ui", "sans-serif"]
      }
    }
  },
  plugins: []
};

export default config;
