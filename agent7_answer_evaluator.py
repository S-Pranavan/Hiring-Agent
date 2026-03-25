"""
agents/agent7_answer_evaluator.py
Agent 7: Answer Evaluation Agent
- Evaluates candidate interview answers using LLM
- Compares against expected answers from knowledge base
- Produces per-question scores and a final composite score
"""

import logging
import json
from dataclasses import dataclass, field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from core.config import settings

logger = logging.getLogger(__name__)


# ─── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class QuestionEvaluation:
    question_order: int
    question_text: str
    candidate_answer: str
    expected_answer: str
    relevance_score: float    # 0–100
    accuracy_score: float     # 0–100
    depth_score: float        # 0–100
    overall_score: float      # weighted
    ai_feedback: str


@dataclass
class EvaluationResult:
    session_id: str
    candidate_id: int
    per_question: list[QuestionEvaluation]
    final_score: float
    summary_feedback: str


# ─── Agent ────────────────────────────────────────────────────────────────────

class AnswerEvaluatorAgent:
    EVAL_PROMPT = """You are an expert technical interviewer and evaluator.

Evaluate the candidate's answer against the expected answer.
Return ONLY valid JSON with this format:
{{
  "relevance_score": <0-100>,
  "accuracy_score": <0-100>,
  "depth_score": <0-100>,
  "overall_score": <0-100>,
  "feedback": "<one to two sentence constructive feedback>"
}}

Scoring guide:
- relevance_score: How well does the answer address the question?
- accuracy_score: How factually correct is the answer?
- depth_score: How deep and detailed is the answer?
- overall_score: Weighted average (relevance 30%, accuracy 40%, depth 30%)
"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.2,
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.EVAL_PROMPT),
            ("human", (
                "Question: {question}\n"
                "Expected Answer: {expected_answer}\n"
                "Candidate Answer: {candidate_answer}"
            )),
        ])
        self.chain = self.prompt | self.llm

    def _evaluate_one(
        self,
        question_text: str,
        expected_answer: str,
        candidate_answer: str,
    ) -> dict:
        response = self.chain.invoke({
            "question": question_text,
            "expected_answer": expected_answer,
            "candidate_answer": candidate_answer,
        })
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)

    def run(
        self,
        session_id: str,
        candidate_id: int,
        questions: list,       # list of InterviewQuestion objects
        answers: list,         # list of CandidateAnswer objects
    ) -> EvaluationResult:
        logger.info(f"[Agent7] Evaluating answers for session {session_id}")

        answer_map = {a.question_order: a.answer_text for a in answers}
        evaluations = []

        for q in questions:
            candidate_ans = answer_map.get(q.order, "No answer provided")

            try:
                scores = self._evaluate_one(
                    question_text=q.text,
                    expected_answer=q.expected_answer,
                    candidate_answer=candidate_ans,
                )
            except Exception as e:
                logger.error(f"[Agent7] Eval error for Q{q.order}: {e}")
                scores = {
                    "relevance_score": 0,
                    "accuracy_score": 0,
                    "depth_score": 0,
                    "overall_score": 0,
                    "feedback": "Evaluation failed.",
                }

            evaluations.append(QuestionEvaluation(
                question_order=q.order,
                question_text=q.text,
                candidate_answer=candidate_ans,
                expected_answer=q.expected_answer,
                relevance_score=float(scores["relevance_score"]),
                accuracy_score=float(scores["accuracy_score"]),
                depth_score=float(scores["depth_score"]),
                overall_score=float(scores["overall_score"]),
                ai_feedback=scores["feedback"],
            ))

        final_score = round(
            sum(e.overall_score for e in evaluations) / max(len(evaluations), 1), 2
        )

        # Generate summary
        strong = [e for e in evaluations if e.overall_score >= 70]
        weak = [e for e in evaluations if e.overall_score < 50]
        summary = (
            f"Candidate scored {final_score}/100 overall. "
            f"Strong in {len(strong)} question(s), struggled with {len(weak)} question(s)."
        )

        return EvaluationResult(
            session_id=session_id,
            candidate_id=candidate_id,
            per_question=evaluations,
            final_score=final_score,
            summary_feedback=summary,
        )
