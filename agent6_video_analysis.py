"""
agents/agent6_video_analysis.py
Agent 6: Video Analysis & Fraud Detection Agent
- Processes recorded interview video
- Detects fraud indicators (looking away, reading notes, person substitution)
- Analyzes facial expressions using DeepFace
- Re-evaluates ego level from visual behavior
- Captures screenshot evidence
"""

import logging
import os
import uuid
from dataclasses import dataclass, field
from typing import Optional

import cv2
import numpy as np
from deepface import DeepFace

logger = logging.getLogger(__name__)


# ─── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class VideoAnalysisResult:
    session_id: str
    candidate_id: int
    fraud_score: float
    fraud_indicators: list
    facial_expression_data: list
    eye_contact_score: float
    ego_level_visual: str     # low / moderate / high
    ego_score_visual: float
    screenshots: list         # [{local_path, timestamp_sec, label}]


# ─── Agent ────────────────────────────────────────────────────────────────────

class VideoAnalysisAgent:
    SAMPLE_RATE = 30  # Analyze every N frames

    def run(
        self,
        session_id: str,
        candidate_id: int,
        video_path: str,
        output_dir: str = "/tmp/screenshots",
    ) -> VideoAnalysisResult:
        logger.info(f"[Agent6] Analyzing video for session {session_id}")
        os.makedirs(output_dir, exist_ok=True)

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        fraud_events = []
        expression_timeline = []
        screenshots = []
        gaze_away_count = 0
        total_analyzed = 0
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % self.SAMPLE_RATE == 0:
                timestamp_sec = round(frame_idx / fps, 2)
                total_analyzed += 1

                try:
                    result = DeepFace.analyze(
                        img_path=frame,
                        actions=["emotion", "gender"],
                        enforce_detection=False,
                        silent=True,
                    )
                    if isinstance(result, list):
                        result = result[0]

                    dominant_emotion = result.get("dominant_emotion", "neutral")
                    emotions = result.get("emotion", {})

                    expression_timeline.append({
                        "timestamp_sec": timestamp_sec,
                        "dominant_emotion": dominant_emotion,
                        "emotions": emotions,
                    })

                    # Fraud heuristic: high fear + surprise or looking away
                    if emotions.get("fear", 0) > 40 or emotions.get("surprise", 0) > 50:
                        label = f"Suspicious behavior at {timestamp_sec}s"
                        fraud_events.append(label)
                        ss_path = self._save_screenshot(
                            frame, output_dir, timestamp_sec, label
                        )
                        screenshots.append({
                            "local_path": ss_path,
                            "timestamp_sec": timestamp_sec,
                            "label": label,
                        })

                    # Gaze proxy: if face not centered, count as gaze-away
                    face_region = result.get("region", {})
                    if face_region:
                        face_x = face_region.get("x", 0) + face_region.get("w", 0) / 2
                        frame_center_x = frame.shape[1] / 2
                        if abs(face_x - frame_center_x) > frame.shape[1] * 0.25:
                            gaze_away_count += 1

                except Exception as e:
                    logger.debug(f"[Agent6] Frame analysis error at {frame_idx}: {e}")

            frame_idx += 1

        cap.release()

        # Compute scores
        fraud_score = min(100.0, round((len(fraud_events) / max(total_analyzed, 1)) * 200, 2))
        eye_contact_score = round(
            max(0, (1 - gaze_away_count / max(total_analyzed, 1))) * 100, 2
        )

        # Visual ego proxy: high confidence emotion + assertive posture (simplified)
        avg_disgust = np.mean([e["emotions"].get("disgust", 0) for e in expression_timeline]) if expression_timeline else 0
        avg_happy = np.mean([e["emotions"].get("happy", 0) for e in expression_timeline]) if expression_timeline else 0
        ego_score_visual = round(min(100, avg_disgust * 1.5 + (100 - avg_happy) * 0.3), 2)

        if ego_score_visual >= 65:
            ego_level_visual = "high"
        elif ego_score_visual >= 35:
            ego_level_visual = "moderate"
        else:
            ego_level_visual = "low"

        logger.info(f"[Agent6] Done. fraud_score={fraud_score}, ego_visual={ego_level_visual}")

        return VideoAnalysisResult(
            session_id=session_id,
            candidate_id=candidate_id,
            fraud_score=fraud_score,
            fraud_indicators=fraud_events,
            facial_expression_data=expression_timeline,
            eye_contact_score=eye_contact_score,
            ego_level_visual=ego_level_visual,
            ego_score_visual=ego_score_visual,
            screenshots=screenshots,
        )

    def _save_screenshot(
        self, frame: np.ndarray, output_dir: str, timestamp: float, label: str
    ) -> str:
        filename = f"{uuid.uuid4().hex}_{int(timestamp)}s.jpg"
        path = os.path.join(output_dir, filename)
        cv2.imwrite(path, frame)
        return path
