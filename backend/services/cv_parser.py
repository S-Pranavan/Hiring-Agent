from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import docx2txt
from docx import Document
from pdfminer.high_level import extract_text as extract_pdf_text


EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"[\+\(]?[0-9][0-9 .\-\(\)]{7,}[0-9]")
SKILL_KEYWORDS = {
    "python": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "next.js": "Next.js",
    "node.js": "Node.js",
    "fastapi": "FastAPI",
    "django": "Django",
    "sql": "SQL",
    "aws": "AWS",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "figma": "Figma",
    "design systems": "Design Systems",
    "user research": "User Research",
    "product thinking": "Product Thinking",
    "leadership": "Leadership",
    "communication": "Communication",
    "collaboration": "Collaboration",
    "analytics": "Analytics",
    "recruiting ops": "Recruiting Ops",
}


class CVParserService:
    def extract_text(self, file_path: str | None) -> str:
        if not file_path:
            return ""
        path = Path(file_path)
        if not path.exists():
            return ""
        suffix = path.suffix.lower()
        try:
            if suffix == ".pdf":
                return extract_pdf_text(str(path)).strip()
            if suffix in {".docx", ".doc"}:
                text = docx2txt.process(str(path)).strip()
                if text:
                    return text
                document = Document(str(path))
                return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()).strip()
            return path.read_text(encoding="utf-8", errors="ignore").strip()
        except Exception:
            return ""

    def parse(self, file_path: str | None, fallback_text: str = "", fallback_name: str = "", fallback_email: str = "", fallback_phone: str = "") -> dict[str, Any]:
        raw_text = self.extract_text(file_path)
        combined_text = raw_text or ""
        if fallback_text:
            combined_text = f"{combined_text}\n{fallback_text}".strip()

        lines = [line.strip() for line in combined_text.splitlines() if line.strip()]
        candidate_name = fallback_name
        if lines:
            first_line = lines[0]
            if 1 <= len(first_line.split()) <= 6 and not any(char.isdigit() for char in first_line[:4]):
                candidate_name = first_line

        email_matches = EMAIL_RE.findall(combined_text)
        phone_matches = PHONE_RE.findall(combined_text)
        lower_text = combined_text.lower()
        found_skills = [label for skill, label in SKILL_KEYWORDS.items() if skill in lower_text]

        summary = ""
        for line in lines:
            if len(line.split()) >= 8:
                summary = line
                break
        if not summary:
            summary = fallback_text.strip() or "Profile received."

        highlights = []
        for line in lines:
            if len(line.split()) >= 5:
                highlights.append(line)
            if len(highlights) == 3:
                break
        if not highlights and fallback_text:
            highlights = [fallback_text.strip()]

        return {
            "candidate_name": candidate_name or fallback_name,
            "email": email_matches[0] if email_matches else fallback_email,
            "phone": phone_matches[0] if phone_matches else fallback_phone,
            "summary": summary,
            "skills": found_skills[:8],
            "highlights": highlights,
            "raw_text": combined_text.strip(),
        }
