-- ============================================================
-- AI HIRING AGENT SYSTEM - DATABASE SCHEMA
-- Version: 1.0.0
-- Engine: PostgreSQL (compatible with SQLite with minor tweaks)
-- ============================================================

-- ============================================================
-- JOBS TABLE
-- ============================================================
CREATE TABLE jobs (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    description     TEXT NOT NULL,
    requirements    TEXT NOT NULL,
    department      VARCHAR(100),
    location        VARCHAR(100),
    employment_type VARCHAR(50) DEFAULT 'full-time',
    status          VARCHAR(20) DEFAULT 'open',  -- open, closed, paused
    created_by      INTEGER,                      -- FK to admin_users
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- CANDIDATES TABLE
-- ============================================================
CREATE TABLE candidates (
    id              SERIAL PRIMARY KEY,
    full_name       VARCHAR(255) NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    phone           VARCHAR(30),
    submission_type VARCHAR(30) NOT NULL,  -- portal, email, registration
    raw_cv_url      TEXT,                  -- S3 URL to original CV file
    cv_format       VARCHAR(10),           -- pdf, docx, doc
    status          VARCHAR(30) DEFAULT 'received',
        -- received, matched, rejected_auto, shortlisted,
        -- scheduled, interviewed, evaluated, selected, rejected_manual
    job_id          INTEGER REFERENCES jobs(id) ON DELETE SET NULL,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- STRUCTURED CVS TABLE
-- ============================================================
CREATE TABLE structured_cvs (
    id                  SERIAL PRIMARY KEY,
    candidate_id        INTEGER REFERENCES candidates(id) ON DELETE CASCADE,
    full_name           VARCHAR(255),
    email               VARCHAR(255),
    phone               VARCHAR(30),
    summary             TEXT,
    skills              JSONB,          -- ["Python", "SQL", "Leadership"]
    experience          JSONB,          -- [{title, company, years, description}]
    education           JSONB,          -- [{degree, institution, year}]
    certifications      JSONB,          -- [{name, issuer, year}]
    languages           JSONB,          -- ["English", "Arabic"]
    raw_text            TEXT,           -- full text extracted from CV
    parsed_at           TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- CV MATCHING RESULTS TABLE
-- ============================================================
CREATE TABLE cv_matching_results (
    id                  SERIAL PRIMARY KEY,
    candidate_id        INTEGER REFERENCES candidates(id) ON DELETE CASCADE,
    job_id              INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    matching_score      DECIMAL(5,2),   -- 0.00 to 100.00
    skill_overlap       JSONB,          -- matched and missing skills
    semantic_vector     JSONB,          -- optional: embedding snapshot
    passed_threshold    BOOLEAN,        -- true if >= 85
    rejection_reason    TEXT,           -- if auto-rejected
    evaluated_at        TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SOFT SKILLS ANALYSIS TABLE
-- ============================================================
CREATE TABLE soft_skills_analysis (
    id                  SERIAL PRIMARY KEY,
    candidate_id        INTEGER REFERENCES candidates(id) ON DELETE CASCADE,
    communication_score DECIMAL(5,2),
    teamwork_score      DECIMAL(5,2),
    leadership_score    DECIMAL(5,2),
    adaptability_score  DECIMAL(5,2),
    overall_score       DECIMAL(5,2),
    extracted_keywords  JSONB,          -- raw keywords detected
    analyzed_at         TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- EGO LEVEL ANALYSIS TABLE (TEXT-BASED)
-- ============================================================
CREATE TABLE ego_text_analysis (
    id                  SERIAL PRIMARY KEY,
    candidate_id        INTEGER REFERENCES candidates(id) ON DELETE CASCADE,
    ego_level           VARCHAR(20),    -- low, moderate, high
    ego_score           DECIMAL(5,2),
    detected_patterns   JSONB,          -- keywords/phrases found
    analyzed_at         TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- INTERVIEW SCHEDULES TABLE
-- ============================================================
CREATE TABLE interview_schedules (
    id                  SERIAL PRIMARY KEY,
    candidate_id        INTEGER REFERENCES candidates(id) ON DELETE CASCADE,
    job_id              INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    interview_type      VARCHAR(20) DEFAULT 'ai',  -- ai, physical
    scheduled_date      DATE,
    scheduled_time      TIME,
    location            TEXT,           -- NULL for AI interviews
    interview_link      TEXT,           -- video interview URL
    confirmation_status VARCHAR(20) DEFAULT 'pending',  -- pending, confirmed, cancelled
    call_attempt_count  INTEGER DEFAULT 0,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- AI INTERVIEW SESSIONS TABLE
-- ============================================================
CREATE TABLE interview_sessions (
    id                  SERIAL PRIMARY KEY,
    candidate_id        INTEGER REFERENCES candidates(id) ON DELETE CASCADE,
    schedule_id         INTEGER REFERENCES interview_schedules(id),
    job_id              INTEGER REFERENCES jobs(id),
    video_url           TEXT,           -- S3 URL to full recording
    duration_seconds    INTEGER,
    started_at          TIMESTAMP,
    ended_at            TIMESTAMP,
    session_status      VARCHAR(20) DEFAULT 'pending'  -- pending, completed, abandoned
);

-- ============================================================
-- INTERVIEW QUESTIONS TABLE
-- ============================================================
CREATE TABLE interview_questions (
    id                  SERIAL PRIMARY KEY,
    session_id          INTEGER REFERENCES interview_sessions(id) ON DELETE CASCADE,
    question_order      INTEGER,
    question_text       TEXT NOT NULL,
    question_type       VARCHAR(30),    -- technical, behavioral, situational
    expected_answer     TEXT,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- CANDIDATE ANSWERS TABLE
-- ============================================================
CREATE TABLE candidate_answers (
    id                  SERIAL PRIMARY KEY,
    session_id          INTEGER REFERENCES interview_sessions(id) ON DELETE CASCADE,
    question_id         INTEGER REFERENCES interview_questions(id),
    answer_text         TEXT,           -- transcript or typed answer
    answer_type         VARCHAR(20),    -- voice, text
    audio_url           TEXT,           -- S3 URL to audio (if voice)
    timestamp_start     INTEGER,        -- seconds into video
    timestamp_end       INTEGER
);

-- ============================================================
-- VIDEO ANALYSIS RESULTS TABLE
-- ============================================================
CREATE TABLE video_analysis_results (
    id                      SERIAL PRIMARY KEY,
    session_id              INTEGER REFERENCES interview_sessions(id) ON DELETE CASCADE,
    candidate_id            INTEGER REFERENCES candidates(id),
    fraud_score             DECIMAL(5,2),           -- 0 = clean, 100 = high fraud
    fraud_indicators        JSONB,                  -- list of detected behaviors
    facial_expression_data  JSONB,                  -- emotions over time
    eye_contact_score       DECIMAL(5,2),
    ego_level_visual        VARCHAR(20),            -- low, moderate, high
    ego_score_visual        DECIMAL(5,2),
    screenshots             JSONB,                  -- [{s3_url, timestamp, label}]
    analyzed_at             TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- ANSWER EVALUATION RESULTS TABLE
-- ============================================================
CREATE TABLE answer_evaluations (
    id                  SERIAL PRIMARY KEY,
    session_id          INTEGER REFERENCES interview_sessions(id) ON DELETE CASCADE,
    candidate_id        INTEGER REFERENCES candidates(id),
    question_id         INTEGER REFERENCES interview_questions(id),
    relevance_score     DECIMAL(5,2),
    accuracy_score      DECIMAL(5,2),
    depth_score         DECIMAL(5,2),
    overall_score       DECIMAL(5,2),
    ai_feedback         TEXT,
    evaluated_at        TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- FINAL CANDIDATE SCORES TABLE
-- ============================================================
CREATE TABLE final_scores (
    id                      SERIAL PRIMARY KEY,
    candidate_id            INTEGER REFERENCES candidates(id) ON DELETE CASCADE,
    job_id                  INTEGER REFERENCES jobs(id),
    cv_match_score          DECIMAL(5,2),
    soft_skills_score       DECIMAL(5,2),
    ego_text_score          DECIMAL(5,2),
    ego_video_score         DECIMAL(5,2),
    fraud_score             DECIMAL(5,2),
    interview_answer_score  DECIMAL(5,2),
    composite_score         DECIMAL(5,2),   -- weighted final score
    recommendation          VARCHAR(20),    -- strong_yes, yes, maybe, no
    computed_at             TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- ADMIN DECISIONS TABLE
-- ============================================================
CREATE TABLE admin_decisions (
    id                  SERIAL PRIMARY KEY,
    candidate_id        INTEGER REFERENCES candidates(id) ON DELETE CASCADE,
    job_id              INTEGER REFERENCES jobs(id),
    admin_id            INTEGER,                    -- FK to admin_users
    decision            VARCHAR(30) NOT NULL,       -- selected, rejected
    decision_type       VARCHAR(30),                -- direct_hire, physical_interview
    offer_joining_date  DATE,
    physical_date       DATE,
    physical_time       TIME,
    physical_location   TEXT,
    notes               TEXT,
    decided_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- COMMUNICATIONS LOG TABLE
-- ============================================================
CREATE TABLE communication_logs (
    id                  SERIAL PRIMARY KEY,
    candidate_id        INTEGER REFERENCES candidates(id),
    comm_type           VARCHAR(20),    -- email, call
    direction           VARCHAR(10),    -- outbound, inbound
    subject             VARCHAR(255),
    body                TEXT,
    status              VARCHAR(20),    -- sent, delivered, failed
    sent_at             TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- ADMIN USERS TABLE
-- ============================================================
CREATE TABLE admin_users (
    id                  SERIAL PRIMARY KEY,
    full_name           VARCHAR(255) NOT NULL,
    email               VARCHAR(255) UNIQUE NOT NULL,
    password_hash       TEXT NOT NULL,
    role                VARCHAR(30) DEFAULT 'recruiter',  -- admin, recruiter
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================
CREATE INDEX idx_candidates_job_id ON candidates(job_id);
CREATE INDEX idx_candidates_status ON candidates(status);
CREATE INDEX idx_cv_matching_candidate ON cv_matching_results(candidate_id);
CREATE INDEX idx_cv_matching_job ON cv_matching_results(job_id);
CREATE INDEX idx_interview_sessions_candidate ON interview_sessions(candidate_id);
CREATE INDEX idx_final_scores_candidate ON final_scores(candidate_id);
CREATE INDEX idx_final_scores_composite ON final_scores(composite_score DESC);
CREATE INDEX idx_communication_logs_candidate ON communication_logs(candidate_id);
