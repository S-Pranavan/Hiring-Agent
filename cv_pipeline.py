"""
pipeline/cv_pipeline.py
Orchestrates the full end-to-end CV processing pipeline:
  Agent 1 → Agent 2 → Agent 3 → Agent 4 (if passed)
Triggered as a background task after CV upload.
"""

import logging
import tempfile
import os

import boto3
from sqlalchemy import text

from core.config import settings
from core.database import AsyncSessionLocal

from agents.agent1_cv_matching import CVMatchingAgent
from agents.agent2_soft_skills import SoftSkillsAnalyzerAgent
from agents.agent3_ego_analyzer import EgoTextAnalyzerAgent
from agents.agent4_interview_scheduler import InterviewSchedulerAgent

logger = logging.getLogger(__name__)

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)


async def run_cv_pipeline(
    candidate_id: int,
    job_id: int,
    s3_url: str,
    file_format: str,
):
    """
    End-to-end pipeline:
    1. Download CV from S3
    2. Run Agent 1 (CV Matching)
    3. If passed → Run Agent 2 (Soft Skills)
    4. Run Agent 3 (Ego Analysis)
    5. Run Agent 4 (Schedule Interview)
    """
    logger.info(f"[Pipeline] Starting for candidate={candidate_id} job={job_id}")

    async with AsyncSessionLocal() as db:
        try:
            # ── Fetch job details ────────────────────────────────────────────
            job_row = await db.execute(
                text("SELECT title, description, requirements FROM jobs WHERE id = :id"),
                {"id": job_id},
            )
            job = job_row.mappings().one()

            # ── Download CV from S3 ──────────────────────────────────────────
            bucket, key = _parse_s3_url(s3_url)
            with tempfile.NamedTemporaryFile(suffix=f".{file_format}", delete=False) as tmp:
                s3.download_fileobj(bucket, key, tmp)
                tmp_path = tmp.name

            # ── Agent 1: CV Matching ─────────────────────────────────────────
            agent1 = CVMatchingAgent()
            match_result = agent1.run(
                candidate_id=candidate_id,
                job_id=job_id,
                file_path=tmp_path,
                file_format=file_format,
                job_description=job["description"],
                job_requirements=job["requirements"],
            )
            os.unlink(tmp_path)

            # Store structured CV
            cv = match_result.structured_cv
            await db.execute(
                text("""
                    INSERT INTO structured_cvs
                    (candidate_id, full_name, email, phone, skills, raw_text)
                    VALUES (:cid, :name, :email, :phone, :skills::jsonb, :raw)
                """),
                {
                    "cid": candidate_id,
                    "name": cv.candidate_name,
                    "email": cv.email,
                    "phone": cv.phone,
                    "skills": str(cv.skills),
                    "raw": cv.raw_text,
                },
            )

            # Store match result
            await db.execute(
                text("""
                    INSERT INTO cv_matching_results
                    (candidate_id, job_id, matching_score, skill_overlap, passed_threshold, rejection_reason)
                    VALUES (:cid, :jid, :score, :overlap::jsonb, :passed, :reason)
                """),
                {
                    "cid": candidate_id,
                    "jid": job_id,
                    "score": match_result.matching_score,
                    "overlap": str(match_result.skill_overlap),
                    "passed": match_result.passed_threshold,
                    "reason": match_result.rejection_reason,
                },
            )

            if not match_result.passed_threshold:
                await _reject_candidate(db, candidate_id, match_result.rejection_reason)
                await db.commit()
                logger.info(f"[Pipeline] Candidate {candidate_id} auto-rejected.")
                return

            # ── Agent 2: Soft Skills ─────────────────────────────────────────
            agent2 = SoftSkillsAnalyzerAgent()
            soft = agent2.run(candidate_id, cv.raw_text)

            await db.execute(
                text("""
                    INSERT INTO soft_skills_analysis
                    (candidate_id, communication_score, teamwork_score,
                     leadership_score, adaptability_score, overall_score, extracted_keywords)
                    VALUES (:cid, :comm, :team, :lead, :adapt, :overall, :kw::jsonb)
                """),
                {
                    "cid": candidate_id,
                    "comm": soft.communication_score,
                    "team": soft.teamwork_score,
                    "lead": soft.leadership_score,
                    "adapt": soft.adaptability_score,
                    "overall": soft.overall_score,
                    "kw": str(soft.extracted_keywords),
                },
            )

            # ── Agent 3: Ego (Text) ──────────────────────────────────────────
            agent3 = EgoTextAnalyzerAgent()
            ego = agent3.run(candidate_id, cv.raw_text)

            await db.execute(
                text("""
                    INSERT INTO ego_text_analysis
                    (candidate_id, ego_level, ego_score, detected_patterns)
                    VALUES (:cid, :level, :score, :patterns::jsonb)
                """),
                {
                    "cid": candidate_id,
                    "level": ego.ego_level,
                    "score": ego.ego_score,
                    "patterns": str(ego.detected_patterns),
                },
            )

            # Update candidate status
            await db.execute(
                text("UPDATE candidates SET status = 'shortlisted' WHERE id = :id"),
                {"id": candidate_id},
            )
            await db.commit()

            # ── Agent 4: Schedule Interview ──────────────────────────────────
            cand_row = await db.execute(
                text("SELECT full_name, email, phone FROM candidates WHERE id = :id"),
                {"id": candidate_id},
            )
            cand = cand_row.mappings().one()

            agent4 = InterviewSchedulerAgent()
            schedule = agent4.run(
                candidate_id=candidate_id,
                job_id=job_id,
                candidate_name=cand["full_name"],
                email=cand["email"],
                phone=cand["phone"],
                job_title=job["title"],
            )

            await db.execute(
                text("""
                    INSERT INTO interview_schedules
                    (candidate_id, job_id, interview_link, confirmation_status)
                    VALUES (:cid, :jid, :link, :status)
                """),
                {
                    "cid": candidate_id,
                    "jid": job_id,
                    "link": schedule.interview_link,
                    "status": schedule.confirmation_status,
                },
            )
            await db.execute(
                text("UPDATE candidates SET status = 'scheduled' WHERE id = :id"),
                {"id": candidate_id},
            )
            await db.commit()

            logger.info(f"[Pipeline] Candidate {candidate_id} fully processed and scheduled.")

        except Exception as e:
            logger.exception(f"[Pipeline] Error for candidate {candidate_id}: {e}")
            await db.rollback()


async def _reject_candidate(db, candidate_id: int, reason: str):
    await db.execute(
        text("UPDATE candidates SET status = 'rejected_auto' WHERE id = :id"),
        {"id": candidate_id},
    )


def _parse_s3_url(url: str) -> tuple[str, str]:
    """Parse s3 https URL into (bucket, key)."""
    # https://bucket.s3.amazonaws.com/key
    parts = url.replace("https://", "").split(".s3.amazonaws.com/")
    return parts[0], parts[1]
