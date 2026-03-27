from __future__ import annotations

import base64
import json
import smtplib
import urllib.parse
import urllib.request
from email.mime.text import MIMEText
from typing import Any

from backend.core.config import settings
from backend.data.store import log_communication


class CommunicationProvider:
    def send_email(self, candidate_id: int, to_email: str, subject: str, body: str) -> dict[str, Any]:
        if settings.smtp_host and settings.smtp_user and settings.smtp_password:
            try:
                message = MIMEText(body, "plain", "utf-8")
                message["Subject"] = subject
                message["From"] = settings.smtp_user
                message["To"] = to_email
                with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
                    server.starttls()
                    server.login(settings.smtp_user, settings.smtp_password)
                    server.sendmail(settings.smtp_user, [to_email], message.as_string())
                log_communication(candidate_id, "email", "outbound", subject, body, "sent", "smtp", {"recipient": to_email})
                return {"status": "sent", "provider": "smtp"}
            except Exception as exc:  # noqa: BLE001
                log_communication(candidate_id, "email", "outbound", subject, body, "failed", "smtp", {"recipient": to_email, "error": str(exc)})
                return {"status": "failed", "provider": "smtp", "error": str(exc)}

        log_communication(candidate_id, "email", "outbound", subject, body, "simulated", "local-fallback", {"recipient": to_email})
        return {"status": "simulated", "provider": "local-fallback"}

    def trigger_call(self, candidate_id: int, to_phone: str, message: str) -> dict[str, Any]:
        if settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_phone_number:
            endpoint = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Calls.json"
            payload = urllib.parse.urlencode(
                {
                    "To": to_phone,
                    "From": settings.twilio_phone_number,
                    "Twiml": f"<Response><Say>{message}</Say></Response>",
                }
            ).encode("utf-8")
            auth = base64.b64encode(f"{settings.twilio_account_sid}:{settings.twilio_auth_token}".encode("utf-8")).decode("utf-8")
            request = urllib.request.Request(
                endpoint,
                data=payload,
                headers={"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    result = json.loads(response.read().decode("utf-8"))
                log_communication(candidate_id, "call", "outbound", "Interview call", message, "sent", "twilio", {"recipient": to_phone, "sid": result.get("sid")})
                return {"status": "sent", "provider": "twilio", "sid": result.get("sid")}
            except Exception as exc:  # noqa: BLE001
                log_communication(candidate_id, "call", "outbound", "Interview call", message, "failed", "twilio", {"recipient": to_phone, "error": str(exc)})
                return {"status": "failed", "provider": "twilio", "error": str(exc)}

        log_communication(candidate_id, "call", "outbound", "Interview call", message, "simulated", "local-fallback", {"recipient": to_phone})
        return {"status": "simulated", "provider": "local-fallback"}
