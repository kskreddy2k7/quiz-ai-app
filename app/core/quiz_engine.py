from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from app.core.ai_engine import AIEngine


@dataclass(frozen=True)
class QuizQuestion:
    topic: str
    difficulty: str
    prompt: str
    choices: List[str]
    answer: str
    explanation: str


class QuizEngine:
    def __init__(self, data_path: Path, ai_engine: AIEngine):
        self.data_path = data_path
        self.ai_engine = ai_engine
        self.difficulty = "easy"

    def load_local_questions(self) -> List[QuizQuestion]:
        try:
            data = json.loads(self.data_path.read_text(encoding="utf-8"))
        except Exception:
            data = []
        questions = [QuizQuestion(**item) for item in data]
        return questions

    def adapt_difficulty(self, percent: int) -> str:
        if percent >= 80:
            self.difficulty = "hard" if self.difficulty == "medium" else "medium"
        elif percent <= 40:
            self.difficulty = "easy"
        return self.difficulty

    def get_local_quiz(self, topic: str, difficulty: str, count: int = 3) -> List[QuizQuestion]:
        questions = self.load_local_questions()
        filtered = [q for q in questions if q.topic.lower() == topic.lower() and q.difficulty == difficulty]
        if len(filtered) < count:
            filtered = [q for q in questions if q.difficulty == difficulty] or questions
        return random.sample(filtered, k=min(count, len(filtered))) if filtered else []

    def request_ai_quiz(
        self,
        topic: str,
        difficulty: str,
        on_complete,
        on_error,
    ) -> None:
        prompt = (
            f"Create 3 multiple-choice questions about {topic} for students. "
            f"Difficulty: {difficulty}. Provide four answer choices, the correct answer, "
            "and a short explanation. Format as JSON list with keys: topic, difficulty, "
            "prompt, choices, answer, explanation."
        )
        system_prompt = "You are a helpful quiz generator for students."

        def handle_complete(text: str) -> None:
            try:
                parsed = json.loads(text)
                questions = [QuizQuestion(**item) for item in parsed]
                on_complete(questions)
            except Exception:
                on_error("AI quiz format issue. Using offline questions.")

        self.ai_engine.run_async(prompt, system_prompt, handle_complete, on_error)

    def get_explanation(self, question: QuizQuestion, selected: str, on_complete, on_error) -> None:
        prompt = (
            f"Explain in simple terms why the correct answer is '{question.answer}' "
            f"for the question: {question.prompt}. The student answered '{selected}'."
        )
        system_prompt = "You are a friendly tutor who explains answers simply."
        self.ai_engine.run_async(prompt, system_prompt, on_complete, on_error)
