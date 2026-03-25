# UI/UX Flow Documentation

---

## 1. CANDIDATE FLOW

### Step 1: Landing Page
- Hero section: "Apply in Minutes – AI-Powered Hiring"
- CTA buttons: "Browse Jobs" | "Submit Your CV"
- Supported submission methods highlighted

### Step 2: Job Discovery
- List of open positions (title, department, location, type)
- Search + filter by department, location, employment type
- Each job card → "View & Apply" button

### Step 3: Job Detail Page
- Full job description + requirements
- "Apply Now" button
- Estimated process timeline shown:
  1. CV Screening (Automated)
  2. AI Interview (Online)
  3. Decision

### Step 4: CV Submission Form
```
Fields:
  [ Full Name        ]
  [ Email Address    ]
  [ Phone Number     ]
  [ Upload CV        ] (PDF or DOCX, max 5MB)
  [ Submit ]
```
- Progress indicator shown after submit
- "You'll hear back within 24 hours" confirmation message

### Step 5: Email / SMS Notification
- Shortlisted → receive call + interview invitation email
- Not shortlisted → receive polite rejection email

### Step 6: AI Interview Page
```
Layout:
  ┌──────────────────────────────────────────────┐
  │  [Company Logo]    AI Interview – [Job Title]│
  ├──────────────────────────────────────────────┤
  │                                              │
  │   Question 3 of 8:                           │
  │   "Describe a time you led a cross-          │
  │    functional project under pressure."       │
  │                                              │
  │   [  Your Camera Feed  ]                     │
  │                                              │
  │   ┌─────────────────────────────────┐        │
  │   │ Type your answer here...        │        │
  │   └─────────────────────────────────┘        │
  │                                              │
  │   [🎤 Record Voice Answer]  [Next Question]  │
  └──────────────────────────────────────────────┘
```
- Timer shown per question (2 minutes recommended)
- Progress bar: Q1 ──●────── Q8
- Voice recording with waveform visualizer

### Step 7: Interview Complete Screen
- "Thank you! Your responses have been submitted."
- "You will receive the result within 3–5 business days."
- Social share (optional): "I just completed an AI interview!"

---

## 2. ADMIN PANEL FLOW

### Login
- Email + Password
- JWT token issued on success

### Dashboard (Home)
```
┌──────────────────────────────────────────────────────┐
│  AI Hiring Dashboard                    [+ New Job]  │
├──────────────┬───────────────────────────────────────┤
│ Total CVs    │ 247                                   │
│ Shortlisted  │ 89                                    │
│ Interviewed  │ 54                                    │
│ Selected     │ 12                                    │
│ Rejected     │ 158                                   │
└──────────────┴───────────────────────────────────────┘

[Pipeline Funnel Chart]
[Recent Activity Feed]
```

### Job Management
```
Jobs List:
┌──────────────────────┬────────────┬────────────┬────────┐
│ Job Title            │ Department │ Applicants │ Status │
├──────────────────────┼────────────┼────────────┼────────┤
│ Senior Backend Eng.  │ Engineering│ 45         │ Open   │
│ Product Manager      │ Product    │ 32         │ Open   │
│ UX Designer          │ Design     │ 28         │ Closed │
└──────────────────────┴────────────┴────────────┴────────┘
[+ Create Job]  [Edit]  [Close]
```

### Create Job Form
```
Fields:
  [ Job Title              ]
  [ Department             ]
  [ Location               ]
  [ Employment Type ▼      ]
  [ Job Description        ] (Rich text editor)
  [ Requirements           ] (Rich text editor)
  [ Publish Job ]
```

### Candidate Pipeline View (per Job)
```
Kanban Columns:
  Received → Matched → Shortlisted → Scheduled → Interviewed → Decision
```
Each candidate card shows:
- Name + email
- Match score badge (e.g., 91%)
- Soft skills score
- Ego level badge (Low 🟢 / Moderate 🟡 / High 🔴)

### Candidate Detail Page
```
┌─────────────────────────────────────────────────┐
│  John Doe – Senior Backend Engineer             │
├──────────────┬──────────────────────────────────┤
│ CV Match     │ ████████░░  91.3%                │
│ Soft Skills  │ ██████░░░░  72.0%                │
│ Ego (Text)   │ Moderate                         │
│ Fraud Score  │ ███░░░░░░░  12.4% (Low risk)     │
│ Interview    │ ████████░░  84.0%                │
│ Final Score  │ █████████░  86.2%  ✅ Strong Yes │
├──────────────┴──────────────────────────────────┤
│  [▶ Watch Interview Recording]                  │
│  [📸 View Fraud Screenshots]                    │
│  [📋 Read Answer Evaluations]                   │
├─────────────────────────────────────────────────┤
│  DECISION:                                      │
│  [✅ Direct Hire]  [📅 Physical Interview]      │
│  [❌ Reject]                                    │
└─────────────────────────────────────────────────┘
```

### Direct Hire Modal
```
  Joining Date: [Date Picker]
  Internal Notes: [Text Area]
  [Send Offer Letter]
```

### Physical Interview Modal
```
  Interview Date: [Date Picker]
  Interview Time: [Time Picker]
  Location:       [Text Field]
  [Schedule & Notify Candidate]
```

### Rejection Modal
```
  Optional Note: [Text Area]
  [Send Rejection Email]
```

### Communication Log (per Candidate)
```
  Timestamp     Type    Subject                  Status
  2026-03-24    Email   Interview Invitation     Sent ✓
  2026-03-24    Call    Shortlist Notification   Answered ✓
  2026-03-20    Email   Application Received     Sent ✓
```
