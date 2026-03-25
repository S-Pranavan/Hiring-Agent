"""
api/routes/admin.py - Admin Decision + Communication Endpoints
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from datetime import date, time

from core.database import get_db
from core.config import settings

router = APIRouter()


# ─── Schemas ──────────────────────────────────────────────────────────────────

class DirectHirePayload(BaseModel):
    candidate_id: int
    job_id: int
    joining_date: date
    admin_notes: Optional[str] = None


class PhysicalInterviewPayload(BaseModel):
    candidate_id: int
    job_id: int
    interview_date: date
    interview_time: time
    location: str
    admin_notes: Optional[str] = None


class RejectPayload(BaseModel):
    candidate_id: int
    job_id: int
    reason: Optional[str] = None


# ─── Email Sender ─────────────────────────────────────────────────────────────

def send_email(to: str, subject: str, html_body: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as s:
        s.starttls()
        s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        s.sendmail(settings.SMTP_USER, to, msg.as_string())


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.post("/decide/direct-hire")
async def direct_hire(payload: DirectHirePayload, db: AsyncSession = Depends(get_db)):
    """Select a candidate and send offer letter with joining date."""
    from sqlalchemy import text

    # Get candidate info
    r = await db.execute(
        text("SELECT full_name, email FROM candidates WHERE id = :id"),
        {"id": payload.candidate_id},
    )
    candidate = r.mappings().one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Log decision
    await db.execute(
        text("""
            INSERT INTO admin_decisions
            (candidate_id, job_id, decision, decision_type, offer_joining_date, notes)
            VALUES (:cid, :jid, 'selected', 'direct_hire', :joining_date, :notes)
        """),
        {
            "cid": payload.candidate_id,
            "jid": payload.job_id,
            "joining_date": payload.joining_date,
            "notes": payload.admin_notes,
        },
    )
    await db.execute(
        text("UPDATE candidates SET status = 'selected' WHERE id = :id"),
        {"id": payload.candidate_id},
    )
    await db.commit()

    # Send offer letter
    html = f"""
    <html><body>
    <h2>Congratulations, {candidate['full_name']}!</h2>
    <p>We are pleased to offer you a position with our company.</p>
    <p><strong>Joining Date:</strong> {payload.joining_date.strftime('%B %d, %Y')}</p>
    <p>Please reply to confirm acceptance. We look forward to welcoming you aboard!</p>
    <p>Best regards,<br>HR Team</p>
    </body></html>
    """
    send_email(candidate["email"], "Job Offer Letter", html)

    return {"message": f"Offer sent to {candidate['email']}", "candidate_id": payload.candidate_id}


@router.post("/decide/physical-interview")
async def schedule_physical_interview(
    payload: PhysicalInterviewPayload,
    db: AsyncSession = Depends(get_db),
):
    """Schedule a physical interview and notify the candidate."""
    from sqlalchemy import text

    r = await db.execute(
        text("SELECT full_name, email, phone FROM candidates WHERE id = :id"),
        {"id": payload.candidate_id},
    )
    candidate = r.mappings().one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    await db.execute(
        text("""
            INSERT INTO admin_decisions
            (candidate_id, job_id, decision, decision_type,
             physical_date, physical_time, physical_location, notes)
            VALUES (:cid, :jid, 'selected', 'physical_interview',
                    :pdate, :ptime, :location, :notes)
        """),
        {
            "cid": payload.candidate_id,
            "jid": payload.job_id,
            "pdate": payload.interview_date,
            "ptime": payload.interview_time,
            "location": payload.location,
            "notes": payload.admin_notes,
        },
    )
    await db.execute(
        text("UPDATE candidates SET status = 'shortlisted' WHERE id = :id"),
        {"id": payload.candidate_id},
    )
    await db.commit()

    html = f"""
    <html><body>
    <h2>Interview Invitation – {candidate['full_name']}</h2>
    <p>You have been selected for an in-person interview!</p>
    <table>
      <tr><td><strong>Date:</strong></td><td>{payload.interview_date}</td></tr>
      <tr><td><strong>Time:</strong></td><td>{payload.interview_time}</td></tr>
      <tr><td><strong>Location:</strong></td><td>{payload.location}</td></tr>
    </table>
    <p>Please confirm your attendance by replying to this email.</p>
    <p>Best regards,<br>HR Team</p>
    </body></html>
    """
    send_email(candidate["email"], "Physical Interview Invitation", html)

    return {"message": "Physical interview scheduled and candidate notified"}


@router.post("/decide/reject")
async def reject_candidate(payload: RejectPayload, db: AsyncSession = Depends(get_db)):
    """Reject a candidate and send automated rejection email."""
    from sqlalchemy import text

    r = await db.execute(
        text("SELECT full_name, email FROM candidates WHERE id = :id"),
        {"id": payload.candidate_id},
    )
    candidate = r.mappings().one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    await db.execute(
        text("""
            INSERT INTO admin_decisions (candidate_id, job_id, decision, notes)
            VALUES (:cid, :jid, 'rejected', :notes)
        """),
        {"cid": payload.candidate_id, "jid": payload.job_id, "notes": payload.reason},
    )
    await db.execute(
        text("UPDATE candidates SET status = 'rejected_manual' WHERE id = :id"),
        {"id": payload.candidate_id},
    )
    await db.commit()

    html = f"""
    <html><body>
    <p>Dear {candidate['full_name']},</p>
    <p>Thank you for applying. After careful consideration, we regret to inform you
    that we will not be moving forward with your application at this time.</p>
    <p>We wish you the best in your job search.</p>
    <p>Kind regards,<br>HR Team</p>
    </body></html>
    """
    send_email(candidate["email"], "Application Update", html)

    return {"message": "Candidate rejected and notified"}


@router.get("/dashboard/summary")
async def dashboard_summary(db: AsyncSession = Depends(get_db)):
    """Get high-level pipeline counts for the admin dashboard."""
    from sqlalchemy import text
    result = await db.execute(text("""
        SELECT status, COUNT(*) as count
        FROM candidates
        GROUP BY status
    """))
    return {row["status"]: row["count"] for row in result.mappings().all()}
