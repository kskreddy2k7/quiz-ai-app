from app.core.config import get_settings
from app.core.logging import logger


class DoubtService:
    """Handle chat-based tutoring responses."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def respond(self, message: str, context: str | None = None) -> tuple[str, list[str]]:
        if self.settings.ai_provider == "openai" and self.settings.openai_api_key:
            try:
                return self._respond_openai(message, context)
            except Exception as exc:  # pragma: no cover
                logger.warning("OpenAI chat failed: %s. Falling back.", exc)

        response = (
            "Great question! Here's a clear breakdown:\n"
            "1) Restate the concept in simple words.\n"
            "2) Connect it to a real-life example.\n"
            "3) Summarize the key takeaway.\n\n"
            "If you share more details, I can tailor the explanation further."
        )
        tips = [
            "Try summarizing the concept in one sentence.",
            "Teach it to a friend to check your understanding.",
        ]
        return response, tips

    def _respond_openai(self, message: str, context: str | None) -> tuple[str, list[str]]:
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        system_prompt = (
            "You are a friendly AI tutor. Provide step-by-step explanations with a positive tone. "
            "Always include 2 concise study tips at the end."
        )
        user_prompt = message
        if context:
            user_prompt = f"Context: {context}\n\nQuestion: {message}"

        response = client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
        )
        content = response.choices[0].message.content or ""
        tips = ["Review the key terms mentioned.", "Practice with a short quiz."]
        return content, tips
