# AI Hiring Agent System

This repo now contains two major pieces:

- A Python/FastAPI hiring-agent backend already present in the project root
- A new root-level Next.js 15 frontend portal for the AI Hiring Agent System

## Frontend highlights

- White-first, enterprise-grade SaaS UI with selective 3D depth effects
- Public pages: landing, about, contact, jobs, job details
- Auth flows: candidate register/login, admin login, hiring team login, forgot password
- Candidate portal: dashboard, profile, apply, tracking, notifications, interviews, AI interview
- Admin portal: dashboard, jobs, candidates, candidate review, interviews, evidence, communications, reports, decisions, settings
- Hiring team portal: dashboard, shortlisted, interview review, comparison, collaboration
- Mock app routes for jobs, dashboard metrics, and application tracking

## Frontend stack

- Next.js 15 App Router
- TypeScript
- Tailwind CSS
- Framer Motion
- Lucide React

## Run the frontend

```bash
npm install
npm run dev
```

Then open [http://localhost:3000](http://localhost:3000).

## Production validation

The new root frontend was verified with:

```bash
npm run build
```

## Backend notes

The existing Python files, API docs, and workflow documents remain in place for the hiring-agent backend and can be integrated further with the new frontend API layer as needed.