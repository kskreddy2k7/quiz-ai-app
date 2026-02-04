from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List

from app.core.ai_engine import AIEngine


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
        try:
            data = json.loads(self.local_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = []
        if not isinstance(data, list):
            data = []
        questions: List[QuizQuestion] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            if not self._is_valid_question(item):
                continue
            questions.append(QuizQuestion(**item))
        return questions

    def save_quiz_offline(self, questions: List[QuizQuestion]):
        data = [q.__dict__ for q in questions]
        self.local_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get_local_quiz(self, subject: str, topic: str, difficulty: str):
        qs = self.load_local_questions()
        if not qs:
            qs = self._demo_questions()
        difficulty = difficulty or self.default_difficulty
        subject_key = subject.strip().lower()
        topic_key = topic.strip().lower()
        matches = []
        for q in qs:
            if q.difficulty != difficulty:
                continue
            topic_value = q.topic.strip().lower()
            if topic_key and topic_value != topic_key:
                continue
            if subject_key and not topic_key and topic_value not in {subject_key, "general"}:
                continue
            matches.append(q)
        return matches[:5]

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
        def success(text: str) -> None:
            try:
                questions = self._parse_ai_response(text, topic or subject, difficulty)
            except ValueError as exc:
                on_error(str(exc))
                return
            self.save_quiz_offline(questions)
            on_complete(questions)

        def fail(msg: str) -> None:
            on_error(msg)

        self.ai.run_async(prompt, "You are an expert teacher.", success, fail)

    def _parse_ai_response(
        self, text: str, topic: str, difficulty: str
    ) -> List[QuizQuestion]:
        raw = text.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw.replace("json", "", 1).strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("AI response was malformed. Using offline quiz.") from exc
        if not isinstance(data, list):
            raise ValueError("AI response was not a list. Using offline quiz.")
        questions: List[QuizQuestion] = []
        for item in data:
            if not isinstance(item, dict):
                raise ValueError("AI response had invalid entries. Using offline quiz.")
            item["topic"] = topic
            item["difficulty"] = difficulty
            if not self._is_valid_question(item):
                raise ValueError("AI response failed validation. Using offline quiz.")
            questions.append(QuizQuestion(**item))
        if not questions:
            raise ValueError("AI returned no questions. Using offline quiz.")
        return questions

    def _is_valid_question(self, item: dict) -> bool:
        required = {"prompt", "choices", "answer", "explanation", "wrong_explanations", "topic", "difficulty"}
        if not required.issubset(item.keys()):
            return False
        if not isinstance(item["choices"], list) or len(item["choices"]) != 4:
            return False
        if item["answer"] not in item["choices"]:
            return False
        if not isinstance(item["wrong_explanations"], dict):
            return False
        for choice in item["choices"]:
            if choice == item["answer"]:
                continue
            if choice not in item["wrong_explanations"]:
                return False
        return True

    def _demo_questions(self) -> List[QuizQuestion]:
        return [
            QuizQuestion(
                topic="Science",
                difficulty="easy",
                prompt="What part of the cell produces energy?",
                choices=["Nucleus", "Mitochondria", "Ribosome", "Golgi body"],
                answer="Mitochondria",
                explanation="Mitochondria generate ATP, the cell's energy currency.",
                wrong_explanations={
                    "Nucleus": "The nucleus stores DNA and controls cell activities.",
                    "Ribosome": "Ribosomes build proteins, not energy.",
                    "Golgi body": "The Golgi packages materials for transport.",
                },
            ),
            QuizQuestion(
                topic="Math",
                difficulty="easy",
                prompt="What is 8 × 7?",
                choices=["54", "56", "63", "64"],
                answer="56",
                explanation="Multiplying 8 by 7 gives 56.",
                wrong_explanations={
                    "54": "8 × 7 is higher than 54.",
                    "63": "63 is 9 × 7, not 8 × 7.",
                    "64": "64 is 8 × 8, not 8 × 7.",
                },
            ),
            QuizQuestion(
                topic="History",
                difficulty="medium",
                prompt="Which ancient civilization built the pyramids of Giza?",
                choices=["Romans", "Egyptians", "Greeks", "Mayans"],
                answer="Egyptians",
                explanation="The pyramids were built by ancient Egyptians as royal tombs.",
                wrong_explanations={
                    "Romans": "Romans came much later and built in Europe.",
                    "Greeks": "Greeks built temples, not the Giza pyramids.",
                    "Mayans": "Mayans built pyramids in the Americas, not Egypt.",
                },
            ),
            QuizQuestion(
                topic="Geography",
                difficulty="easy",
                prompt="Which planet is known as the Red Planet?",
                choices=["Mars", "Venus", "Jupiter", "Saturn"],
                answer="Mars",
                explanation="Mars looks red because of iron oxide on its surface.",
                wrong_explanations={
                    "Venus": "Venus appears yellowish due to thick clouds.",
                    "Jupiter": "Jupiter is a gas giant with stripes.",
                    "Saturn": "Saturn is known for its rings, not red color.",
                },
            ),
            QuizQuestion(
                topic="Technology",
                difficulty="medium",
                prompt="Which language is primarily used for Android development today?",
                choices=["Kotlin", "Swift", "Ruby", "Go"],
                answer="Kotlin",
                explanation="Kotlin is the modern, officially supported Android language.",
                wrong_explanations={
                    "Swift": "Swift is primarily used for iOS development.",
                    "Ruby": "Ruby isn't a standard language for Android apps.",
                    "Go": "Go is not the primary Android app language.",
                },
            ),
        ]
