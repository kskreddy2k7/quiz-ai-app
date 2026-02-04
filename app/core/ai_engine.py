from __future__ import annotations

import os
from typing import Callable

from openai import OpenAI

from app.core.utils import run_in_thread


class AIEngine:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self._refresh_client()

    def _refresh_client(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def is_available(self) -> bool:
        self._refresh_client()
        return self.client is not None

    def availability_message(self) -> str:
        self._refresh_client()
        if not self.api_key:
            return "AI Mode: Offline 📴 (no API key)"
        return "AI Mode: Online ✨"

    def _friendly_error(self, exc: Exception | None = None) -> str:
        if not self.api_key:
            return "📴 AI is offline. Add an OpenAI API key to enable AI features."
        if exc:
            message = str(exc).lower()
            if "connection" in message or "timeout" in message or "network" in message:
                return "📴 AI is unavailable. Check your internet connection."
        return "🤖 AI is unavailable right now. Please try again later."

    def run_async(
        self,
        prompt: str,
        system_prompt: str,
        on_complete: Callable[[str], None],
        on_error: Callable[[str], None],
    ) -> None:
        self._refresh_client()

        def task() -> str:
            if not self.client:
                raise RuntimeError("missing api key")

            res = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
                max_tokens=900,
            )
            return res.choices[0].message.content.strip()

        run_in_thread(
            task,
            on_complete,
            lambda message: on_error(self._friendly_error(Exception(message))),
        )
