class DoubtSolver:
    def __init__(self, ai_engine):
        self.ai = ai_engine

    def solve(self, question, on_complete, on_error):
        prompt = f"Explain this clearly to a student:\n{question}"
        self.ai.run_async(prompt, "You are a helpful tutor.", on_complete, on_error)
