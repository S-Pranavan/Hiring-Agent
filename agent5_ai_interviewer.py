"""
agents/agent5_ai_interviewer.py
Agent 5: AI Interviewer + Question Generator
- Uses LLM (via LangChain) to generate personalized interview questions
- Supports voice (Whisper STT) and text answers
- Stores questions, answers, and video recording references
"""

import logging
import json
from dataclasses import dataclass, field
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import openai

from core.config import settings

logger = logging.getLogger(__name__)


# ─── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class InterviewQuestion:
    order: int
    text: str
    question_type: str  # technical / behavioral / situational
    expected_answer: str


@dataclass
class CandidateAnswer:
    question_order: int
    answer_text: str
    answer_type: str   # voice / text
    audio_url: Optional[str] = None


@dataclass
class InterviewSession:
    session_id: str
    candidate_id: int
    job_id: int
    questions: list[InterviewQuestion] = field(default_factory=list)
    answers: list[CandidateAnswer] = field(default_factory=list)
    video_url: Optional[str] = None


# ─── Question Generator ───────────────────────────────────────────────────────

class QuestionGeneratorAgent:
    SYSTEM_PROMPT = """You are a senior technical recruiter.
Generate a structured list of interview questions tailored to the candidate's CV
and the specific job role. Return ONLY valid JSON.

Format:
[
  {{
    "order": 1,
    "text": "...",
    "type": "technical|behavioral|situational",
    "expected_answer": "..."
  }}
]

Rules:
- Generate exactly 8 questions
- Mix: 3 technical, 3 behavioral, 2 situational
- Reference specific skills or experience from the CV
- Expected answers should be concise bullet points
"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            ("human", "Job Role: {job_title}\nJob Description: {job_description}\n\nCandidate CV Summary:\n{cv_summary}"),
        ])
        self.chain = self.prompt | self.llm

    def generate(
        self,
        job_title: str,
        job_description: str,
        cv_summary: str,
    ) -> list[InterviewQuestion]:
        logger.info("[Agent5] Generating interview questions via LLM")

        response = self.chain.invoke({
            "job_title": job_title,
            "job_description": job_description,
            "cv_summary": cv_summary,
        })

        raw = response.content.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        questions_data = json.loads(raw)

        return [
            InterviewQuestion(
                order=q["order"],
                text=q["text"],
                question_type=q["type"],
                expected_answer=q["expected_answer"],
            )
            for q in questions_data
        ]


# ─── Speech-to-Text ───────────────────────────────────────────────────────────

class SpeechToText:
    def transcribe(self, audio_file_path: str) -> str:
        logger.info(f"[Agent5] Transcribing audio: {audio_file_path}")
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
            )
        return transcript


# ─── Main Agent ───────────────────────────────────────────────────────────────

class AIInterviewerAgent:
    def __init__(self):
        self.question_generator = QuestionGeneratorAgent()
        self.stt = SpeechToText()

    def prepare_session(
        self,
        session_id: str,
        candidate_id: int,
        job_id: int,
        job_title: str,
        job_description: str,
        cv_raw_text: str,
    ) -> InterviewSession:
        session = InterviewSession(
            session_id=session_id,
            candidate_id=candidate_id,
            job_id=job_id,
        )

        # Build CV summary (first 1000 chars for prompt efficiency)
        cv_summary = cv_raw_text[:1000]

        session.questions = self.question_generator.generate(
            job_title=job_title,
            job_description=job_description,
            cv_summary=cv_summary,
        )

        logger.info(f"[Agent5] Session {session_id} prepared with {len(session.questions)} questions")
        return session

    def process_voice_answer(
        self,
        session: InterviewSession,
        question_order: int,
        audio_path: str,
        audio_s3_url: str,
    ) -> CandidateAnswer:
        text = self.stt.transcribe(audio_path)
        answer = CandidateAnswer(
            question_order=question_order,
            answer_text=text,
            answer_type="voice",
            audio_url=audio_s3_url,
        )
        session.answers.append(answer)
        return answer

    def process_text_answer(
        self,
        session: InterviewSession,
        question_order: int,
        text: str,
    ) -> CandidateAnswer:
        answer = CandidateAnswer(
            question_order=question_order,
            answer_text=text,
            answer_type="text",
        )
        session.answers.append(answer)
        return answer
