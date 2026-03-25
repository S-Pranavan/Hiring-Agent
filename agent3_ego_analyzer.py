"""
agents/agent3_ego_analyzer.py
Agent 3: Ego Level Analyzer (Text-Based)
- Detects language patterns indicative of ego level
- Classifies as Low / Moderate / High
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ─── Ego Indicator Banks ──────────────────────────────────────────────────────

HIGH_EGO_INDICATORS = [
    "i alone", "i single-handedly", "i was the only one",
    "without me", "my idea", "i invented", "i built everything",
    "i am the best", "i outperformed everyone", "i never fail",
    "i am exceptional", "i am superior", "i revolutionized",
    "i am irreplaceable", "i deserve", "i demand",
]

MODERATE_EGO_INDICATORS = [
    "i led", "i drove", "i achieved", "i delivered",
    "i improved", "i designed", "i built", "i created",
    "i managed", "i owned", "i launched", "i increased",
]

LOW_EGO_INDICATORS = [
    "we collaborated", "our team", "we achieved", "together",
    "supported", "assisted", "contributed", "helped the team",
    "worked alongside", "we built", "collective effort",
    "credit to the team", "team success",
]


# ─── Data Class ───────────────────────────────────────────────────────────────

@dataclass
class EgoTextResult:
    candidate_id: int
    ego_level: str        # low / moderate / high
    ego_score: float      # 0–100
    detected_patterns: dict


# ─── Agent ────────────────────────────────────────────────────────────────────

class EgoTextAnalyzerAgent:

    def _count_matches(self, text: str, indicators: list) -> list:
        text_lower = text.lower()
        return [ind for ind in indicators if ind in text_lower]

    def run(self, candidate_id: int, cv_text: str) -> EgoTextResult:
        logger.info(f"[Agent3] Ego analysis for candidate {candidate_id}")

        high_found   = self._count_matches(cv_text, HIGH_EGO_INDICATORS)
        moderate_found = self._count_matches(cv_text, MODERATE_EGO_INDICATORS)
        low_found    = self._count_matches(cv_text, LOW_EGO_INDICATORS)

        # Scoring: high ego patterns raise score, low ego patterns lower it
        raw_score = (
            (len(high_found) * 20)
            + (len(moderate_found) * 5)
            - (len(low_found) * 8)
        )
        # Normalize to 0–100
        ego_score = max(0.0, min(100.0, float(raw_score)))

        if ego_score >= 65:
            ego_level = "high"
        elif ego_score >= 35:
            ego_level = "moderate"
        else:
            ego_level = "low"

        return EgoTextResult(
            candidate_id=candidate_id,
            ego_level=ego_level,
            ego_score=round(ego_score, 2),
            detected_patterns={
                "high_ego": high_found,
                "moderate_ego": moderate_found,
                "low_ego_collaborative": low_found,
            },
        )
