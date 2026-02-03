import json
import random
import re
from typing import Iterable

from app.core.config import get_settings
from app.core.logging import logger
from app.schemas import IncorrectExplanation, QuizItem


SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


class QuizService:
    """Generate quizzes from source text using AI or heuristic fallbacks."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def generate(self, text: str, num_questions: int, difficulty: str) -> list[QuizItem]:
        if self.settings.ai_provider == "openai" and self.settings.openai_api_key:
            try:
                return self._generate_with_openai(text, num_questions, difficulty)
            except Exception as exc:  # pragma: no cover - depends on external service
                logger.warning("OpenAI generation failed: %s. Falling back.", exc)

        return self._generate_fallback(text, num_questions, difficulty)

    def _generate_with_openai(
        self, text: str, num_questions: int, difficulty: str
    ) -> list[QuizItem]:
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        prompt = (
            "You are an AI tutor. Create {num} multiple-choice questions from the text. "
            "Include 4 options, one correct answer, a step-by-step explanation, and short "
            "reasons why each incorrect option is wrong. Difficulty: {difficulty}. "
            "Return JSON list with keys question, options, answer, explanation, incorrect_explanations "
            "(list of objects with option and reason). Text: {text}"
        ).format(num=num_questions, difficulty=difficulty, text=text)

        response = client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        content = response.choices[0].message.content or "[]"
        return _parse_quiz_items(content)

    def _generate_fallback(
        self, text: str, num_questions: int, difficulty: str
    ) -> list[QuizItem]:
        sentences = [s.strip() for s in SENTENCE_SPLIT.split(text) if len(s.strip()) > 20]
        if not sentences:
            sentences = [text.strip()]

        random.shuffle(sentences)
        samples = list(_chunked(sentences, 4))
        questions: list[QuizItem] = []

        for chunk in samples:
            if len(questions) >= num_questions:
                break
            if len(chunk) < 2:
                continue
            correct = chunk[0]
            distractors = _build_distractors(chunk[1:], correct)
            options = _ensure_four_options(correct, distractors)

            questions.append(
                QuizItem(
                    question=_build_question(correct, difficulty),
                    options=options,
                    answer=correct,
                    explanation=_build_explanation(correct, difficulty),
                    incorrect_explanations=[
                        IncorrectExplanation(
                            option=option,
                            reason="This detail is not supported by the provided text.",
                        )
                        for option in options
                        if option != correct
                    ],
                )
            )

        return questions[:num_questions]


def _build_question(sentence: str, difficulty: str) -> str:
    prefix = {
        "easy": "Which statement is clearly supported by the text?",
        "medium": "Which option best summarizes this idea from the passage?",
        "hard": "Which statement most accurately reflects the passage's nuance?",
    }[difficulty]
    return f"{prefix}\n\n{sentence[:160].strip()}"


def _build_explanation(sentence: str, difficulty: str) -> str:
    steps = [
        "Step 1: Identify the key idea in the passage.",
        "Step 2: Match the option that repeats that idea without changing meaning.",
        "Step 3: Confirm the option aligns with the difficulty focus.",
    ]
    detail = f"The correct option echoes: '{sentence[:140].strip()}...'"
    if difficulty == "hard":
        detail += " It preserves the subtle qualifiers in the source text."
    return "\n".join([*steps, detail])


def _build_distractors(sentences: list[str], correct: str) -> list[str]:
    candidates = [sentence for sentence in sentences if sentence and sentence != correct]
    if len(candidates) < 3:
        candidates.extend(
            [
                "This option overgeneralizes the passage.",
                "This option introduces an unrelated detail.",
                "This option reverses the meaning of the statement.",
            ]
        )
    return candidates[:3]


def _ensure_four_options(correct: str, distractors: list[str]) -> list[str]:
    options = [correct, *distractors[:3]]
    unique = list(dict.fromkeys(options))
    while len(unique) < 4:
        unique.append(f"Not supported by the text ({len(unique) + 1}).")
    random.shuffle(unique)
    return unique


def _chunked(items: list[str], size: int) -> Iterable[list[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _parse_quiz_items(raw: str) -> list[QuizItem]:
    cleaned = _extract_json(raw)
    data = json.loads(cleaned)
    return [QuizItem(**item) for item in data]


def _extract_json(raw: str) -> str:
    if raw.strip().startswith("["):
        return raw
    start = raw.find("[")
    end = raw.rfind("]")
    if start == -1 or end == -1:
        return "[]"
    return raw[start : end + 1]
