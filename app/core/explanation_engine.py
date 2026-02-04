from __future__ import annotations

from app.core.ai_engine import AIEngine


class ExplanationEngine:
    def __init__(self, ai_engine: AIEngine):
        self.ai = ai_engine

    def request_explanation(self, q, selected, on_complete, on_error) -> None:
        try:
            base_explanation = self._base_explanation(q, selected)
        except Exception:
            on_error("Unable to load explanation. Please try again.")
            return

        if not self.ai.is_available():
            on_complete(base_explanation)
            return

        prompt = (
            "Rewrite this explanation in a friendly, concise way for students. "
            f"Explanation: {base_explanation}"
        )

        def success(text: str) -> None:
            cleaned = text.strip()
            on_complete(cleaned if cleaned else base_explanation)

        def fail(_msg: str) -> None:
            on_complete(base_explanation)

        self.ai.run_async(prompt, "You are a supportive tutor.", success, fail)

    def _base_explanation(self, q, selected: str) -> str:
        if selected == q.answer:
            return q.explanation or "That answer is correct."
        return q.wrong_explanations.get(
            selected,
            "That option is incorrect because it does not match the concept in the question.",
        )

    def fallback_explanation(self, q, selected: str) -> str:
        return self._base_explanation(q, selected)
