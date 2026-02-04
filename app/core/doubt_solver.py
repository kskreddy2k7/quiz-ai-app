from __future__ import annotations

from typing import Callable

from app.core.ai_engine import AIEngine


class DoubtSolver:
    def __init__(self, ai_engine: AIEngine) -> None:
        self.ai_engine = ai_engine

    def solve(
        self,
        question: str,
        on_complete: Callable[[str], None],
        on_error: Callable[[str], None],
    ) -> None:
        if not self.ai_engine.is_available():
            on_error("AI features unavailable. Configure API key.")
            return
        system_prompt = (
            "You are a friendly AI tutor for students. "
            "Explain step-by-step, keep it simple, and stay within educational scope."
        )
        self.ai_engine.run_async(question, system_prompt, on_complete, on_error)
