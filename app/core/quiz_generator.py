from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List

from app.core.ai_engine import AIEngine
from app.core.utils import run_in_thread


@dataclass
class QuizQuestion:
    prompt: str
    choices: List[str]
    answer: str
    explanation: str
    wrong_explanations: Dict[str, str]
    topic: str
    difficulty: str


class QuizGenerator:
    def __init__(self, ai_engine: AIEngine, local_path: Path):
        self.ai = ai_engine
        self.local_path = local_path
        self.default_difficulty = "easy"
        self.local_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.local_path.exists():
            self.local_path.write_text("[]", encoding="utf-8")

    # ---------- OFFLINE ----------
    def load_local_questions(self) -> List[QuizQuestion]:
        data = json.loads(self.local_path.read_text(encoding="utf-8"))
        return [QuizQuestion(**q) for q in data]

    def save_quiz_offline(self, questions: List[QuizQuestion]):
        data = [q.__dict__ for q in questions]
        self.local_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get_local_quiz(self, subject: str, topic: str, difficulty: str):
        qs = self.load_local_questions()
        difficulty = difficulty or self.default_difficulty
        return [q for q in qs if q.difficulty == difficulty][:5]

    # ---------- AI ----------
    def request_ai_quiz(
        self,
        subject: str,
        topic: str,
        difficulty: str,
        on_complete: Callable,
        on_error: Callable,
    ):
        prompt = f"""
Create 5 MCQ questions.

Subject: {subject}
Topic: {topic or "General"}
Difficulty: {difficulty}

Return ONLY JSON:

[
 {{
  "prompt": "...",
  "choices": ["A","B","C","D"],
  "answer": "Correct option",
  "explanation": "Why correct",
  "wrong_explanations": {{
    "Wrong option": "Why wrong"
  }}
 }}
]
"""

        def task():
            result = []

            def success(text: str):
                nonlocal result
                raw = text.strip().strip("```").replace("json", "")
                data = json.loads(raw)
                for i in data:
                    result.append(
                        QuizQuestion(
                            prompt=i["prompt"],
                            choices=i["choices"],
                            answer=i["answer"],
                            explanation=i["explanation"],
                            wrong_explanations=i["wrong_explanations"],
                            topic=topic or subject,
                            difficulty=difficulty,
                        )
                    )
                self.save_quiz_offline(result)

            def fail(msg: str):
                raise RuntimeError(msg)

            self.ai.run_async(prompt, "You are an expert teacher.", success, fail)
            return result

        run_in_thread(task, on_complete, on_error)
