from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

from app.core.ai_engine import AIEngine
from app.core.utils import run_in_thread


@dataclass
class QuizQuestion:
    prompt: str
    choices: List[str]
    answer: str
    explanation: str
    topic: str
    difficulty: str


class QuizGenerator:
    def __init__(self, ai_engine: AIEngine, local_path: Path) -> None:
        self.ai_engine = ai_engine
        self.local_path = local_path
        self.default_difficulty = "easy"

    def load_local_questions(self) -> List[QuizQuestion]:
        if not self.local_path.exists():
            return []
        data = json.loads(self.local_path.read_text(encoding="utf-8"))
        questions = []
        for item in data:
            questions.append(
                QuizQuestion(
                    prompt=item["prompt"],
                    choices=item["choices"],
                    answer=item["answer"],
                    explanation=item["explanation"],
                    topic=item.get("topic", "General"),
                    difficulty=item.get("difficulty", "easy"),
                )
            )
        return questions

    def get_local_quiz(self, subject: str, topic: str, difficulty: str) -> List[QuizQuestion]:
        difficulty = difficulty or self.default_difficulty
        questions = self.load_local_questions()
        subject_lower = subject.lower()
        topic_lower = topic.lower()
        filtered = [
            q
            for q in questions
            if q.difficulty == difficulty
            and (subject_lower in q.topic.lower() or topic_lower in q.topic.lower())
        ]
        if len(filtered) >= 3:
            return filtered[:5]
        fallback = [q for q in questions if q.difficulty == difficulty]
        return (filtered + fallback)[:5]

    def request_ai_quiz(
        self,
        subject: str,
        topic: str,
        difficulty: str,
        on_complete: Callable[[List[QuizQuestion]], None],
        on_error: Callable[[str], None],
    ) -> None:
        prompt = (
            "Create 5 multiple-choice questions for students. "
            f"Subject: {subject}. Topic: {topic}. Difficulty: {difficulty}. "
            "Return ONLY valid JSON as a list. Each item must have: "
            "prompt (string), choices (list of 4 strings), answer (string), explanation (string)."
        )

        def task() -> List[QuizQuestion]:
            response = self.ai_engine._complete(prompt, "You generate student-friendly quizzes.")
            raw = response.strip()
            if raw.startswith("```"):
                raw = raw.strip("`")
            data = json.loads(raw)
            questions: List[QuizQuestion] = []
            for item in data:
                questions.append(
                    QuizQuestion(
                        prompt=item["prompt"],
                        choices=item["choices"],
                        answer=item["answer"],
                        explanation=item["explanation"],
                        topic=topic or subject,
                        difficulty=difficulty,
                    )
                )
            return questions

        run_in_thread(task, on_complete, on_error)
