from __future__ import annotations

from typing import Callable, Optional
from app.services.ai_service import AIService
from app.services.quiz_service import QuizQuestion


class TutorService:
    """
    Handles AI interactions involved in teaching:
    1. Solving specific doubts (Chat).
    2. Explaining quiz answers (Feedback).
    """

    def __init__(self, ai_service: AIService):
        self.ai = ai_service

    # --- Doubt Solving ---

    def solve_doubt(self, question: str, on_complete: Callable[[str], None], on_error: Callable[[str], None]) -> None:
        question = question.strip()
        if not question:
            on_error("Please enter a question.")
            return

        if not self.ai.is_available():
            on_error(self.ai.availability_message())
            return

        self.ai.solve_doubt(question, on_complete, on_error)

    # --- Quiz Explanations ---

    def explain_answer(
        self, question: QuizQuestion, selected_option: str, on_complete: Callable[[str], None], on_error: Callable[[str], None]
    ) -> None:
        """
        Provides a personalized explanation for the user's answer.
        """
        # Base logic (instant local feedback)
        is_correct = (selected_option == question.answer)
        base_text = question.explanation if is_correct else question.wrong_explanations.get(selected_option, "Incorrect.")

        # If offline or simple, just return base
        if not self.ai.is_available():
            on_complete(base_text)
            return

        # Backend AI explanation
        def success(text: str):
            on_complete(text.strip())
            
        def fail(_msg: str):
            # Fallback silently to base text
            on_complete(base_text)

        self.ai.explain_answer(
            question_text=question.prompt,
            correct_answer=question.answer,
            user_answer=selected_option,
            on_complete=success,
            on_error=fail
        )
