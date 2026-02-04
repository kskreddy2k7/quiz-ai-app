from __future__ import annotations

from typing import Callable

from app.core.ai_engine import AIEngine
from app.core.quiz_generator import QuizQuestion
from app.core.utils import run_in_thread


class ExplanationEngine:
    def __init__(self, ai_engine: AIEngine) -> None:
        self.ai_engine = ai_engine

    def fallback_explanation(self, question: QuizQuestion, selected: str) -> str:
        if selected == question.answer:
            return (
                f"Your answer '{selected}' is correct because {question.explanation} "
                "Keep noticing the key concept behind the question."
            )
        return (
            f"Your answer '{selected}' is incorrect because it does not match the core idea. "
            f"The correct answer is '{question.answer}' because {question.explanation}"
        )

    def request_explanation(
        self,
        question: QuizQuestion,
        selected_answer: str,
        on_complete: Callable[[str], None],
        on_error: Callable[[str], None],
    ) -> None:
        if not self.ai_engine.is_available():
            on_error("AI unavailable")
            return
        prompt = (
            "Explain the answer to this question for a student. "
            "Always include: why the selected answer is wrong, and why the correct answer is right. "
            f"Question: {question.prompt} "
            f"Choices: {', '.join(question.choices)} "
            f"Selected: {selected_answer} "
            f"Correct: {question.answer}. "
            "Use simple language and be encouraging."
        )

        def task() -> str:
            return self.ai_engine._complete(prompt, "You are a patient teacher.")

        run_in_thread(task, on_complete, on_error)
