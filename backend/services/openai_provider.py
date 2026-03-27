from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from backend.core.config import settings


def _fallback_questions(job_title: str, department: str, skill_hint: str) -> list[dict[str, Any]]:
    return [
        {
            "order": 1,
            "text": f"Tell us about a project where you used {skill_hint} to improve outcomes.",
            "question_type": "behavioral",
            "expected_answer": "Describe context, action, collaboration, and measurable outcome.",
            "guidance": "Use a specific example with impact and shared ownership.",
        },
        {
            "order": 2,
            "text": f"How would you build trust in an AI-assisted workflow for the {job_title} role?",
            "question_type": "situational",
            "expected_answer": "Explain transparency, evidence, and human decision points.",
            "guidance": "Focus on reviewer confidence and explainability.",
        },
        {
            "order": 3,
            "text": f"What trade-offs would you make to deliver fast without lowering quality in {department}?",
            "question_type": "technical",
            "expected_answer": "Discuss prioritization, iteration, guardrails, and metrics.",
            "guidance": "Balance speed with reliability.",
        },
    ]


class OpenAIProvider:
    def __init__(self) -> None:
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def generate_questions(self, job_title: str, department: str, skill_hint: str, cv_summary: str) -> list[dict[str, Any]]:
        if not self.enabled:
            return _fallback_questions(job_title, department, skill_hint)

        prompt = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Generate exactly 3 interview questions as JSON. Each item must include order, text, question_type, expected_answer, guidance."},
                {"role": "user", "content": f"Job title: {job_title}\nDepartment: {department}\nSkill hint: {skill_hint}\nCandidate summary: {cv_summary}\nReturn only JSON array."},
            ],
            "temperature": 0.4,
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(prompt).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
            content = payload["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                parts = content.split("```")
                content = parts[1]
                if content.startswith("json"):
                    content = content[4:]
            questions = json.loads(content)
            if isinstance(questions, list) and questions:
                return questions
        except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError):
            pass
        return _fallback_questions(job_title, department, skill_hint)

    def evaluate_answer(self, question: str, expected_answer: str, candidate_answer: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        prompt = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Evaluate the candidate answer. Return only JSON with relevance_score, accuracy_score, depth_score, overall_score, feedback."},
                {"role": "user", "content": f"Question: {question}\nExpected: {expected_answer}\nAnswer: {candidate_answer}"},
            ],
            "temperature": 0.1,
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(prompt).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
            content = payload["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                parts = content.split("```")
                content = parts[1]
                if content.startswith("json"):
                    content = content[4:]
            result = json.loads(content)
            return {
                "relevance_score": float(result["relevance_score"]),
                "accuracy_score": float(result["accuracy_score"]),
                "depth_score": float(result["depth_score"]),
                "overall_score": float(result["overall_score"]),
                "feedback": str(result["feedback"]),
            }
        except (urllib.error.URLError, KeyError, IndexError, ValueError, json.JSONDecodeError):
            return None
