from app.core.logging import logger
from app.schemas import IncorrectExplanation, QuizItem
from app.services.ai_client import AIClient


class QuizService:
    """Generate quizzes from source text using AI or heuristic fallbacks."""

    def __init__(self) -> None:
        self.client = AIClient()

    def generate(
        self, text: str, num_questions: int, difficulty: str, subject: str
    ) -> list[QuizItem]:
        logger.info(
            "Generating %s quiz questions (difficulty: %s, subject: %s).",
            num_questions,
            difficulty,
            subject,
        )
        return self._generate_with_openai(text, num_questions, difficulty, subject)

    def _generate_with_openai(
        self, text: str, num_questions: int, difficulty: str, subject: str
    ) -> list[QuizItem]:
        system_prompt = (
            "You are ChatGPT, an expert AI tutor who creates engaging MCQ quizzes with emojis 🎯✅❌. "
            "Return JSON with keys topic and questions. Each question must include: "
            "question (string), options (array of 4 strings), answer (string), "
            "explanation (string explaining why the correct answer is correct), "
            "incorrect_explanations (array of objects with option and reason explaining why each wrong option is wrong)."
        )
        user_prompt = (
            f"Subject focus: {subject}\n"
            f"Create {num_questions} {difficulty} MCQs from the study content below. "
            "Use emojis in the questions and explanations, keep wording student-friendly, "
            "and ensure each incorrect option has a unique reason.\n\n"
            f"Study content:\n{text}"
        )

        payload = self.client.chat_json(system_prompt, user_prompt, temperature=0.4)
        questions_raw = payload.get("questions", [])

        if not isinstance(questions_raw, list) or not questions_raw:
            raise ValueError("AI did not return any quiz questions.")

        questions: list[QuizItem] = []
        for item in questions_raw:
            options = list(item.get("options", []))
            incorrect_explanations = [
                IncorrectExplanation(**wrong) for wrong in item.get("incorrect_explanations", [])
            ]
            questions.append(
                QuizItem(
                    question=str(item.get("question", "")).strip(),
                    options=options,
                    answer=str(item.get("answer", "")).strip(),
                    explanation=str(item.get("explanation", "")).strip(),
                    incorrect_explanations=incorrect_explanations,
                )
            )

        return questions
