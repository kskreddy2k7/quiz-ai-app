from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

from app.core.ai_engine import AIEngine
from app.core.utils import run_in_thread


# -------------------------
# DATA MODEL
# -------------------------

@dataclass
class QuizQuestion:
    prompt: str
    choices: List[str]
    answer: str
    explanation: str
    topic: str
    difficulty: str


# -------------------------
# QUIZ GENERATOR
# -------------------------

class QuizGenerator:
    def __init__(self, ai_engine: AIEngine, local_path: Path) -> None:
        self.ai_engine = ai_engine
        self.local_path = local_path
        self.default_difficulty = "easy"

        if not self.local_path.exists():
            self._create_empty_file()

    # -------------------------
    # LOCAL QUESTIONS
    # -------------------------

    def load_local_questions(self) -> List[QuizQuestion]:
        try:
            data = json.loads(self.local_path.read_text(encoding="utf-8"))
        except Exception:
            return []

        questions: List[QuizQuestion] = []
        for item in data:
            questions.append(
                QuizQuestion(
                    prompt=item["prompt"],
                    choices=item["choices"],
                    answer=item["answer"],
                    explanation=item.get("explanation", ""),
                    topic=item.get("topic", "General"),
                    difficulty=item.get("difficulty", self.default_difficulty),
                )
            )
        return questions

    def get_local_quiz(
        self, subject: str, topic: str, difficulty: str
    ) -> List[QuizQuestion]:
        difficulty = difficulty or self.default_difficulty
        questions = self.load_local_questions()

        subject_l = subject.lower()
        topic_l = topic.lower() if topic else ""

        filtered = [
            q
            for q in questions
            if q.difficulty == difficulty
            and (subject_l in q.topic.lower() or topic_l in q.topic.lower())
        ]

        if len(filtered) >= 3:
            return filtered[:5]

        fallback = [q for q in questions if q.difficulty == difficulty]
        return (filtered + fallback)[:5]

    # -------------------------
    # AI QUIZ GENERATION
    # -------------------------

    def request_ai_quiz(
        self,
        subject: str,
        topic: str,
        difficulty: str,
        on_complete: Callable[[List[QuizQuestion]], None],
        on_error: Callable[[str], None],
    ) -> None:
        difficulty = difficulty or self.default_difficulty

        prompt = f"""
Create exactly 5 multiple-choice questions for students.

Subject: {subject}
Topic: {topic or "General"}
Difficulty: {difficulty}

Rules:
- Each question must have exactly 4 options
- Clearly specify the correct answer
- Provide a short explanation
- Use simple student-friendly language
- Output ONLY valid JSON in this format:

[
  {{
    "prompt": "Question text",
    "choices": ["A", "B", "C", "D"],
    "answer": "Correct option text",
    "explanation": "Why this answer is correct"
  }}
]
"""

        def task() -> List[QuizQuestion]:
            result: List[QuizQuestion] = []

            def on_ai_complete(text: str):
                nonlocal result
                raw = text.strip()

                # Remove markdown fences if AI adds them
                if raw.startswith("```"):
                    raw = raw.strip("`").strip()
                    if raw.startswith("json"):
                        raw = raw[4:].strip()

                data = json.loads(raw)
                for item in data:
                    result.append(
                        QuizQuestion(
                            prompt=item["prompt"],
                            choices=item["choices"],
                            answer=item["answer"],
                            explanation=item.get("explanation", ""),
                            topic=topic or subject,
                            difficulty=difficulty,
                        )
                    )

            def on_ai_error(message: str):
                raise RuntimeError(message)

            self.ai_engine.run_async(
                prompt,
                "You are an expert teacher who creates clear MCQ quizzes.",
                on_ai_complete,
                on_ai_error,
            )

            return result

        run_in_thread(task, on_complete, on_error)

    # -------------------------
    # FILE INIT
    # -------------------------

    def _create_empty_file(self) -> None:
        self.local_path.parent.mkdir(parents=True, exist_ok=True)
        self.local_path.write_text("[]", encoding="utf-8")
