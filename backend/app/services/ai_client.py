import json
from typing import Any

from openai import OpenAI

from app.core.config import get_settings
from app.core.logging import logger


class AIClient:
    """Centralized OpenAI client for JSON-first tutoring workflows."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = (
            OpenAI(api_key=self.settings.openai_api_key)
            if self.settings.openai_api_key
            else None
        )

    def chat_json(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.4
    ) -> dict[str, Any]:
        if not self.client:
            raise ValueError(
                "OpenAI API key is missing. Please set OPENAI_API_KEY in the environment."
            )
        try:
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                response_format={"type": "json_object"},
            )
        except Exception as exc:  # pragma: no cover - depends on external API
            logger.error("OpenAI request failed: %s", exc)
            raise ValueError("AI generation failed. Please try again shortly.") from exc

        content = response.choices[0].message.content or "{}"
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:  # pragma: no cover - depends on model output
            logger.error("Failed to parse AI JSON response: %s", content)
            raise ValueError("AI response could not be parsed. Please try again.") from exc
