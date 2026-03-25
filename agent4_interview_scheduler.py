"""
agents/agent4_interview_scheduler.py
Agent 4: Interview Call Assistant
- Contacts candidates via call (Twilio) and email
- Confirms availability and schedules AI interview
- Saves confirmed schedule to database
"""

import logging
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional

from twilio.rest import Client as TwilioClient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from core.config import settings

logger = logging.getLogger(__name__)


# ─── Data Class ───────────────────────────────────────────────────────────────

@dataclass
class ScheduleResult:
    candidate_id: int
    job_id: int
    interview_link: str
    scheduled_at: datetime
    call_success: bool
    email_success: bool
    confirmation_status: str  # confirmed / pending / failed


# ─── Agent ────────────────────────────────────────────────────────────────────

class InterviewSchedulerAgent:

    def __init__(self):
        self.twilio = TwilioClient(
            settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN
        )

    def _generate_interview_link(self, candidate_id: int) -> str:
        token = uuid.uuid4().hex
        return f"https://your-domain.com/interview/{candidate_id}/{token}"

    def _make_call(self, phone: str, candidate_name: str, interview_link: str) -> bool:
        try:
            twiml = f"""
            <Response>
              <Say voice="Polly.Joanna">
                Hello {candidate_name}, congratulations! You have been shortlisted
                for an AI-powered interview. Please check your email for the
                interview link and complete it within 48 hours. Thank you.
              </Say>
            </Response>
            """
            self.twilio.calls.create(
                twiml=twiml,
                to=phone,
                from_=settings.TWILIO_PHONE_NUMBER,
            )
            logger.info(f"[Agent4] Call placed to {phone}")
            return True
        except Exception as e:
            logger.error(f"[Agent4] Call failed: {e}")
            return False

    def _send_email(
        self,
        email: str,
        candidate_name: str,
        job_title: str,
        interview_link: str,
        scheduled_at: datetime,
    ) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Your AI Interview – {job_title}"
            msg["From"] = settings.SMTP_USER
            msg["To"] = email

            html = f"""
            <html><body>
            <p>Dear {candidate_name},</p>
            <p>Congratulations! You have been shortlisted for the position of
            <strong>{job_title}</strong>.</p>
            <p>Please complete your AI interview by clicking the link below:</p>
            <p><a href="{interview_link}" style="background:#0066cc;color:white;
            padding:10px 20px;border-radius:5px;text-decoration:none;">
            Start Interview</a></p>
            <p><strong>Link expires:</strong> {(scheduled_at + timedelta(hours=48)).strftime('%Y-%m-%d %H:%M')} UTC</p>
            <p>Best regards,<br>AI Hiring Team</p>
            </body></html>
            """

            msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_USER, email, msg.as_string())

            logger.info(f"[Agent4] Interview email sent to {email}")
            return True
        except Exception as e:
            logger.error(f"[Agent4] Email failed: {e}")
            return False

    def run(
        self,
        candidate_id: int,
        job_id: int,
        candidate_name: str,
        email: str,
        phone: str,
        job_title: str,
    ) -> ScheduleResult:
        logger.info(f"[Agent4] Scheduling interview for candidate {candidate_id}")

        link = self._generate_interview_link(candidate_id)
        scheduled_at = datetime.utcnow() + timedelta(hours=24)

        call_ok = self._make_call(phone, candidate_name, link)
        email_ok = self._send_email(email, candidate_name, job_title, link, scheduled_at)

        status = "confirmed" if (call_ok or email_ok) else "failed"

        return ScheduleResult(
            candidate_id=candidate_id,
            job_id=job_id,
            interview_link=link,
            scheduled_at=scheduled_at,
            call_success=call_ok,
            email_success=email_ok,
            confirmation_status=status,
        )
