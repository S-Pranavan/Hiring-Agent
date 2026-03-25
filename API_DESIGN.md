# AI Hiring Agent System - API Design
# Full Endpoint Reference

Base URL: `https://api.your-domain.com/api/v1`

---

## Authentication

All endpoints (except `/health` and `/api/v1/candidates/upload`) require:

```
Authorization: Bearer <JWT_TOKEN>
```

---

## 1. Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/jobs/` | Create a new job opening |
| GET | `/jobs/` | List all jobs (filter: ?status=open) |
| GET | `/jobs/{job_id}` | Get job details |
| PATCH | `/jobs/{job_id}/status` | Update job status (open/closed/paused) |

### POST /jobs/
**Request Body:**
```json
{
  "title": "Senior Backend Engineer",
  "description": "We are looking for...",
  "requirements": "5+ years Python, AWS experience...",
  "department": "Engineering",
  "location": "Remote",
  "employment_type": "full-time"
}
```
**Response:** `201 Created` with job object

---

## 2. Candidates

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/candidates/upload` | Upload CV via web portal (multipart/form-data) |
| GET | `/candidates/` | List candidates (filter: ?job_id=1&status=shortlisted) |
| GET | `/candidates/{id}/profile` | Full candidate profile + all AI scores |

### POST /candidates/upload
**Form Data:**
```
job_id        (int)
full_name     (string)
email         (string)
phone         (string)
cv_file       (file: PDF or DOCX)
```
**Response:** `202 Accepted`
```json
{
  "message": "CV received. Processing started.",
  "candidate_id": 42
}
```

### GET /candidates/{id}/profile
**Response:**
```json
{
  "candidate": { "id": 42, "full_name": "John Doe", "status": "shortlisted", ... },
  "cv_matching": { "matching_score": 91.3, "passed_threshold": true, ... },
  "soft_skills": { "communication_score": 78, "leadership_score": 65, "overall_score": 72, ... },
  "ego_text": { "ego_level": "moderate", "ego_score": 42, ... },
  "final_score": { "composite_score": 84.5, "recommendation": "yes", ... }
}
```

---

## 3. Interviews

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/interviews/session/start` | Start an interview session |
| GET | `/interviews/session/{session_id}/questions` | Get questions for session |
| POST | `/interviews/session/{session_id}/answer/text` | Submit text answer |
| POST | `/interviews/session/{session_id}/answer/voice` | Upload audio answer |
| POST | `/interviews/session/{session_id}/complete` | Mark session complete + upload video |
| GET | `/interviews/session/{session_id}/results` | Get evaluation results |

### POST /interviews/session/start
**Request Body:**
```json
{
  "candidate_id": 42,
  "job_id": 7,
  "schedule_id": 15
}
```
**Response:**
```json
{
  "session_id": "abc123def456",
  "questions": [
    {
      "order": 1,
      "text": "Can you walk me through your experience with Python microservices?",
      "type": "technical"
    }
  ]
}
```

### POST /interviews/session/{session_id}/answer/voice
**Form Data:**
```
question_order  (int)
audio_file      (file: mp3/wav/webm)
```

---

## 4. Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/dashboard/summary` | Pipeline status counts |
| POST | `/admin/decide/direct-hire` | Select candidate → send offer letter |
| POST | `/admin/decide/physical-interview` | Schedule physical interview |
| POST | `/admin/decide/reject` | Reject candidate → send rejection email |

### POST /admin/decide/direct-hire
```json
{
  "candidate_id": 42,
  "job_id": 7,
  "joining_date": "2026-05-01",
  "admin_notes": "Strong candidate, fast track"
}
```

### POST /admin/decide/physical-interview
```json
{
  "candidate_id": 42,
  "job_id": 7,
  "interview_date": "2026-04-10",
  "interview_time": "10:00:00",
  "location": "123 Main St, Office Floor 3"
}
```

---

## 5. Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/webhooks/email-cv` | Ingest CV from monitored email inbox |

### POST /webhooks/email-cv
Called by the email monitor service when a new CV email arrives.
```json
{
  "sender_email": "john@example.com",
  "sender_name": "John Doe",
  "subject": "Application for Senior Backend Engineer",
  "attachment_s3_url": "https://...",
  "attachment_format": "pdf",
  "job_id": 7
}
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request – invalid input |
| 401 | Unauthorized – missing/invalid JWT |
| 403 | Forbidden – insufficient permissions |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

## Rate Limits

| Endpoint Group | Limit |
|----------------|-------|
| CV Upload | 100 req/min per IP |
| Admin decisions | 500 req/min |
| Interview sessions | 50 req/min per candidate |
