from app.core.logging import logger
from app.services.ai_client import AIClient


class DoubtService:
    """Handle chat-based tutoring responses."""

    def __init__(self) -> None:
        self.client = AIClient()

    def respond(
        self, message: str, subject: str, context: str | None = None
    ) -> tuple[str, list[str]]:
        logger.info("Generating AI doubt response for subject: %s", subject)
        system_prompt = (
            "You are ChatGPT, an expert AI tutor for school students. Explain concepts clearly, "
            "step-by-step, with a friendly tone and helpful emojis like 📘✨🧠. "
            "Support Physics, Chemistry, Maths, Biology, and Computer Science. "
            "Return JSON with keys response (string) and tips (array of 2-4 short study tips). "
            "In the response, always include: the correct answer, why it is correct, and a short "
            "section that lists common incorrect answers (or misconceptions) and why they are wrong."
        )
        user_prompt = (
            f"Subject: {subject}\n"
            f"Student Question: {message}\n"
            f"Context (if any): {context or 'None'}\n"
            "Explain why the answer makes sense and include a quick recap at the end. "
            "Format sections clearly with labels like ✅ Correct Answer and ❌ Why Common Answers Are Wrong."
        )
        payload = self.client.chat_json(system_prompt, user_prompt, temperature=0.5)

        response = str(payload.get("response", "")).strip()
        tips_raw = payload.get("tips", [])
        tips = [str(tip).strip() for tip in tips_raw if str(tip).strip()]
        if not response:
            raise ValueError("AI response was empty. Please try again with more detail.")

        return response, tips
