# AI Hiring Agent System - Agent Workflows

---

## Pipeline Overview

```
CV Received
    │
    ▼
[Agent 1] CV–Job Matching
    │
    ├── Score < 85% ──► Auto-Reject + Email
    │
    └── Score ≥ 85%
            │
            ▼
       [Agent 2] Soft Skills Analyzer
            │
            ▼
       [Agent 3] Ego Level Analyzer (Text)
            │
            ▼
       [Agent 4] Interview Scheduler
            │
            ▼
       [Agent 5] AI Interviewer + Question Generator
            │
            ▼
       [Agent 6] Video Analysis + Fraud Detection
            │
            ▼
       [Agent 7] Answer Evaluator
            │
            ▼
       Final Score Computed
            │
            ▼
       Admin Review Panel
            │
       ┌────┴────┐
       │         │
    Select     Reject
       │         │
  ┌────┴───┐   Rejection
  │        │    Email
Direct  Physical
 Hire   Interview
  │        │
Offer   Call +
Letter  Email
```

---

## Agent 1: CV–Job Matching Agent

**Trigger:** New CV submitted (any channel)

**Steps:**
1. Download CV from S3
2. Extract raw text (PDF → pdfminer, DOCX → docx2txt)
3. Parse structured fields (name, email, skills, experience)
4. Tokenize CV text + Job Description via BERT tokenizer
5. Generate embeddings using `all-MiniLM-L6-v2`
6. Calculate cosine similarity score
7. Apply threshold: ≥ 85% → pass, < 85% → reject
8. Store structured CV + matching result in DB

**Inputs:** CV file (S3 URL), Job Description text, Job Requirements text
**Outputs:** MatchingResult (score, structured CV, passed flag)
**SLA:** < 30 seconds

---

## Agent 2: Soft Skills Analyzer

**Trigger:** Agent 1 passes (score ≥ 85%)

**Steps:**
1. Receive structured CV raw text
2. Scan for soft skill keywords per category:
   - Communication: 12 indicators
   - Teamwork: 11 indicators
   - Leadership: 13 indicators
   - Adaptability: 13 indicators
3. Calculate per-category score (found/total * 100)
4. Calculate overall average score
5. Store in `soft_skills_analysis` table

**Inputs:** CV raw text, candidate_id
**Outputs:** SoftSkillsResult (4 category scores + overall)
**SLA:** < 5 seconds

---

## Agent 3: Ego Level Analyzer (Text)

**Trigger:** Runs in parallel with Agent 2

**Steps:**
1. Scan CV for high-ego language patterns (e.g., "I alone", "I built everything")
2. Scan for moderate-ego patterns (e.g., "I led", "I achieved")
3. Scan for collaborative/low-ego patterns (e.g., "we achieved", "our team")
4. Compute raw score: (high × 20) + (moderate × 5) − (low × 8)
5. Normalize to 0–100
6. Classify: < 35 = Low, 35–64 = Moderate, ≥ 65 = High
7. Store in `ego_text_analysis` table

**Inputs:** CV raw text, candidate_id
**Outputs:** EgoTextResult (ego_level, ego_score, patterns)
**SLA:** < 3 seconds

---

## Agent 4: Interview Call Assistant

**Trigger:** Candidate passes Agents 1–3

**Steps:**
1. Generate unique interview link with session token
2. Place outbound call via Twilio with TwiML announcement
3. Send HTML interview invitation email via SMTP
4. Record call attempt count
5. Save schedule to `interview_schedules` table
6. Update candidate status to `scheduled`

**Inputs:** candidate_id, job_id, name, email, phone, job_title
**Outputs:** ScheduleResult (link, datetime, call/email status)
**SLA:** < 10 seconds

---

## Agent 5: AI Interviewer + Question Generator

**Trigger:** Candidate opens interview link

**Steps:**
1. Load session from DB (candidate CV, job description)
2. Call GPT-4o via LangChain to generate 8 custom questions:
   - 3 technical (based on CV skills)
   - 3 behavioral (based on experience)
   - 2 situational (based on job requirements)
3. Present questions one by one on screen with video recording active
4. For each answer:
   - Voice: Record audio → upload to S3 → transcribe via Whisper
   - Text: Accept typed input directly
5. Store questions + answers + video URL in DB
6. Mark session complete

**Inputs:** candidate_id, job_id, CV text, job description
**Outputs:** InterviewSession (questions, answers, video_url)
**SLA:** Real-time (interview duration: 15–30 min)

---

## Agent 6: Video Analysis & Fraud Detection

**Trigger:** Interview session marked complete

**Steps:**
1. Download video from S3
2. Sample every 30 frames (≈1 sec intervals)
3. For each frame:
   - Run DeepFace emotion analysis
   - Check gaze direction (face center vs frame center)
   - Detect fraud indicators (high fear/surprise emotion spikes)
   - Capture screenshot if fraud detected
4. Compute fraud score (fraud events / total frames × 200)
5. Compute eye contact score
6. Compute visual ego score from emotion averages
7. Upload screenshots to S3
8. Store all results in `video_analysis_results` table

**Inputs:** video file (S3 URL), session_id, candidate_id
**Outputs:** VideoAnalysisResult (fraud_score, ego_visual, screenshots)
**SLA:** < 5 minutes

---

## Agent 7: Answer Evaluation Agent

**Trigger:** Agent 6 completes

**Steps:**
1. Load all questions + candidate answers from DB
2. For each question-answer pair:
   - Call GPT-4o with evaluation prompt
   - Receive: relevance_score, accuracy_score, depth_score, feedback
3. Compute per-question overall score (weighted average)
4. Compute session final score (average of all question scores)
5. Generate summary feedback string
6. Store in `answer_evaluations` table
7. Compute composite final score across all agents
8. Store in `final_scores` table

**Inputs:** session_id, candidate_id, questions[], answers[]
**Outputs:** EvaluationResult (per-question scores, final_score, summary)
**SLA:** < 3 minutes

---

## Final Score Computation

```
composite_score =
  (cv_match_score        × 0.25) +
  (soft_skills_score     × 0.15) +
  (interview_score       × 0.35) +
  (100 - fraud_score)    × 0.15) +
  (100 - ego_text_score) × 0.05) +
  (100 - ego_video_score × 0.05)

Recommendation:
  ≥ 85 → strong_yes
  70–84 → yes
  55–69 → maybe
  < 55  → no
```
