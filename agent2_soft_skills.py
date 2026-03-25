"""
agents/agent2_soft_skills.py
Agent 2: Interpersonal Skills Analyzer
- Analyzes CV text for soft skills using keyword extraction + NLP
- Returns scored soft skills breakdown
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ─── Skill Keyword Bank ───────────────────────────────────────────────────────

SKILL_KEYWORDS = {
    "communication": [
        "communication", "presentation", "public speaking", "written",
        "verbal", "negotiation", "articulate", "reporting", "persuasion",
        "stakeholder", "briefing", "documentation",
    ],
    "teamwork": [
        "teamwork", "collaboration", "cross-functional", "cooperative",
        "partnered", "worked with", "joint", "team player", "ensemble",
        "group project", "coordinated",
    ],
    "leadership": [
        "leadership", "led", "managed", "mentored", "coached", "directed",
        "supervised", "team lead", "head of", "spearheaded", "initiated",
        "founded", "established",
    ],
    "adaptability": [
        "adaptable", "flexible", "fast learner", "quick learner", "self-taught",
        "resourceful", "versatile", "agile", "multitask", "pivot", "change",
        "ambiguity", "dynamic",
    ],
}


# ─── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class SoftSkillsResult:
    candidate_id: int
    communication_score: float
    teamwork_score: float
    leadership_score: float
    adaptability_score: float
    overall_score: float
    extracted_keywords: dict


# ─── Agent ────────────────────────────────────────────────────────────────────

class SoftSkillsAnalyzerAgent:

    def _score_category(self, text: str, keywords: list) -> tuple[float, list]:
        text_lower = text.lower()
        found = [kw for kw in keywords if kw in text_lower]
        max_possible = len(keywords)
        score = min(round((len(found) / max_possible) * 100, 2), 100.0)
        return score, found

    def run(self, candidate_id: int, cv_text: str) -> SoftSkillsResult:
        logger.info(f"[Agent2] Analyzing soft skills for candidate {candidate_id}")

        scores = {}
        found_keywords = {}

        for category, keywords in SKILL_KEYWORDS.items():
            score, found = self._score_category(cv_text, keywords)
            scores[category] = score
            found_keywords[category] = found

        overall = round(sum(scores.values()) / len(scores), 2)

        return SoftSkillsResult(
            candidate_id=candidate_id,
            communication_score=scores["communication"],
            teamwork_score=scores["teamwork"],
            leadership_score=scores["leadership"],
            adaptability_score=scores["adaptability"],
            overall_score=overall,
            extracted_keywords=found_keywords,
        )
