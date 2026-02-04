class ExplanationEngine:
    def __init__(self, ai_engine):
        self.ai = ai_engine

    def request_explanation(self, q, selected, on_complete, on_error):
        try:
            if selected == q.answer:
                on_complete(q.explanation)
            else:
                on_complete(
                    q.wrong_explanations.get(selected, self.fallback_explanation(q, selected))
                )
        except Exception:
            on_error("Unable to load explanation. Please try again.")

    def fallback_explanation(self, q, selected: str) -> str:
        if selected == q.answer:
            return q.explanation or "That answer is correct."
        return "That option is incorrect because it does not match the concept in the question."
