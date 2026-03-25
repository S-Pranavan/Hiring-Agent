# AI Hiring Agent System - Project Folder Structure

```
ai_hiring_system/
│
├── README.md                          # Project overview & setup guide
├── requirements.txt                   # All Python dependencies
├── .env.example                       # Environment variables template
├── docker-compose.yml                 # Local dev stack
│
├── docs/
│   ├── PRD.md                         # Product Requirements Document
│   ├── ARCHITECTURE.md                # System architecture overview
│   ├── API_DESIGN.md                  # Full API endpoint reference
│   └── AGENT_WORKFLOWS.md             # Per-agent workflow diagrams
│
├── database/
│   ├── schema.sql                     # Full PostgreSQL schema
│   └── migrations/                    # Alembic migration files
│       └── versions/
│
├── backend/
│   ├── main.py                        # FastAPI app entry point
│   │
│   ├── core/
│   │   ├── config.py                  # Settings (env vars)
│   │   ├── database.py                # Async SQLAlchemy setup
│   │   ├── security.py                # JWT auth
│   │   └── logging.py                 # Structured logging
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── jobs.py                # Job CRUD endpoints
│   │       ├── candidates.py          # CV upload & tracking
│   │       ├── interviews.py          # Interview session endpoints
│   │       ├── admin.py               # Admin decisions & comms
│   │       └── webhooks.py            # Email ingest webhook
│   │
│   ├── pipeline/
│   │   ├── cv_pipeline.py             # Main orchestrator (Agents 1–4)
│   │   └── interview_pipeline.py      # Interview orchestrator (Agents 5–7)
│   │
│   └── services/
│       ├── s3_service.py              # S3 upload/download helpers
│       ├── email_service.py           # SMTP + IMAP email monitor
│       └── call_service.py            # Twilio call helpers
│
├── agents/
│   ├── agent1_cv_matching.py          # CV parsing + semantic matching
│   ├── agent2_soft_skills.py          # Soft skills NLP analyzer
│   ├── agent3_ego_analyzer.py         # Ego level text classifier
│   ├── agent4_interview_scheduler.py  # Auto-scheduler via call/email
│   ├── agent5_ai_interviewer.py       # LLM question gen + STT
│   ├── agent6_video_analysis.py       # Fraud detection + face analysis
│   └── agent7_answer_evaluator.py     # LLM answer scoring
│
├── ui_flows/
│   ├── candidate_flow.md              # Candidate UX journey
│   └── admin_flow.md                  # Admin panel UX journey
│
└── deployment/
    ├── Dockerfile                     # Container build
    ├── docker-compose.yml             # Dev environment
    ├── nginx.conf                     # Reverse proxy config
    └── aws/
        ├── ec2_setup.sh               # EC2 server bootstrap
        └── s3_policy.json             # S3 bucket IAM policy
```
