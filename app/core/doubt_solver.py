from __future__ import annotations

from app.core.ai_engine import AIEngine


class DoubtSolver:
    def __init__(self, ai_engine: AIEngine):
        self.ai = ai_engine

    def solve(self, question: str, on_complete, on_error) -> None:
        question = question.strip()
        if not question:
            on_error("Please enter a question to ask the tutor.")
            return
        if not self.ai.is_available():
            on_error("📴 AI tutor is offline. Try the quiz mode or come back later.")
            return
        prompt = f"Explain this clearly to a student:\n{question}"
        self.ai.run_async(prompt, "You are a helpful tutor.", on_complete, on_error)
