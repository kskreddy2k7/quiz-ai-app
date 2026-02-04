class ExplanationEngine:
    def __init__(self, ai_engine):
        self.ai = ai_engine

    def request_explanation(self, q, selected, on_complete, on_error):
        if selected == q.answer:
            on_complete(q.explanation)
        else:
            on_complete(q.wrong_explanations.get(selected, "This option is incorrect."))class ExplanationEngine:
    def __init__(self, ai_engine):
        self.ai = ai_engine

    def request_explanation(self, q, selected, on_complete, on_error):
        if selected == q.answer:
            on_complete(q.explanation)
        else:
            on_complete(q.wrong_explanations.get(selected, "This option is incorrect."))
