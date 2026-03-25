"""
agents/agent1_cv_matching.py
Agent 1: CV–Job Matching Agent
- Parses CV text
- Computes semantic similarity to Job Description using BERT
- Applies 85% threshold
"""

import re
import json
import logging
from dataclasses import dataclass, field
from typing import Optional

import torch
from transformers import AutoTokenizer, AutoModel
from pdfminer.high_level import extract_text as extract_pdf_text
import docx2txt

logger = logging.getLogger(__name__)

# ─── Model Setup ─────────────────────────────────────────────────────────────

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_tokenizer = None
_model = None


def _load_model():
    global _tokenizer, _model
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModel.from_pretrained(MODEL_NAME)
        _model.eval()


# ─── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class StructuredCV:
    candidate_name: str = ""
    email: str = ""
    phone: str = ""
    summary: str = ""
    skills: list = field(default_factory=list)
    experience: list = field(default_factory=list)
    education: list = field(default_factory=list)
    certifications: list = field(default_factory=list)
    languages: list = field(default_factory=list)
    raw_text: str = ""


@dataclass
class MatchingResult:
    candidate_id: int
    job_id: int
    matching_score: float
    passed_threshold: bool
    skill_overlap: dict
    structured_cv: StructuredCV
    rejection_reason: Optional[str] = None


# ─── CV Parser ────────────────────────────────────────────────────────────────

class CVParser:
    EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    PHONE_RE = re.compile(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]")

    def extract_text(self, file_path: str, fmt: str) -> str:
        if fmt == "pdf":
            return extract_pdf_text(file_path)
        elif fmt in ("docx", "doc"):
            return docx2txt.process(file_path)
        else:
            raise ValueError(f"Unsupported format: {fmt}")

    def parse(self, raw_text: str) -> StructuredCV:
        cv = StructuredCV()
        cv.raw_text = raw_text

        # Extract email
        emails = self.EMAIL_RE.findall(raw_text)
        if emails:
            cv.email = emails[0]

        # Extract phone
        phones = self.PHONE_RE.findall(raw_text)
        if phones:
            cv.phone = phones[0]

        # Skill extraction (extend keyword list per industry)
        skill_keywords = [
            "python", "java", "javascript", "typescript", "sql", "nosql",
            "machine learning", "deep learning", "nlp", "computer vision",
            "react", "vue", "angular", "fastapi", "django", "flask",
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
            "leadership", "communication", "teamwork", "agile", "scrum",
            "project management", "data analysis", "excel", "power bi",
        ]
        text_lower = raw_text.lower()
        cv.skills = [sk for sk in skill_keywords if sk in text_lower]

        # Extract name (first non-empty line heuristic)
        for line in raw_text.split("\n"):
            stripped = line.strip()
            if stripped and len(stripped.split()) <= 5 and not stripped[0].isdigit():
                cv.candidate_name = stripped
                break

        return cv


# ─── Semantic Matcher ─────────────────────────────────────────────────────────

class SemanticMatcher:
    def __init__(self):
        _load_model()

    def _embed(self, text: str) -> torch.Tensor:
        inputs = _tokenizer(
            text, return_tensors="pt", truncation=True,
            max_length=512, padding=True
        )
        with torch.no_grad():
            output = _model(**inputs)
        # Mean pool
        return output.last_hidden_state.mean(dim=1)

    def compute_similarity(self, cv_text: str, jd_text: str) -> float:
        emb_cv = self._embed(cv_text)
        emb_jd = self._embed(jd_text)
        cos = torch.nn.functional.cosine_similarity(emb_cv, emb_jd)
        return round(float(cos.item()) * 100, 2)

    def skill_overlap(self, cv_skills: list, jd_text: str) -> dict:
        jd_lower = jd_text.lower()
        matched = [s for s in cv_skills if s in jd_lower]
        missing = [s for s in cv_skills if s not in jd_lower]
        return {"matched": matched, "missing": missing}


# ─── Main Agent ───────────────────────────────────────────────────────────────

class CVMatchingAgent:
    THRESHOLD = 85.0

    def __init__(self):
        self.parser = CVParser()
        self.matcher = SemanticMatcher()

    def run(
        self,
        candidate_id: int,
        job_id: int,
        file_path: str,
        file_format: str,
        job_description: str,
        job_requirements: str,
    ) -> MatchingResult:
        logger.info(f"[Agent1] Processing candidate {candidate_id} for job {job_id}")

        # Step 1: Extract text
        raw_text = self.parser.extract_text(file_path, file_format)

        # Step 2: Parse structure
        structured_cv = self.parser.parse(raw_text)

        # Step 3: Compute match
        jd_combined = f"{job_description}\n{job_requirements}"
        score = self.matcher.compute_similarity(raw_text, jd_combined)
        overlap = self.matcher.skill_overlap(structured_cv.skills, jd_combined)

        passed = score >= self.THRESHOLD
        reason = None if passed else f"CV match score {score:.1f}% below threshold {self.THRESHOLD}%"

        logger.info(f"[Agent1] Candidate {candidate_id} score={score} passed={passed}")

        return MatchingResult(
            candidate_id=candidate_id,
            job_id=job_id,
            matching_score=score,
            passed_threshold=passed,
            skill_overlap=overlap,
            structured_cv=structured_cv,
            rejection_reason=reason,
        )
