from __future__ import annotations

import os
import threading
from typing import Callable

from openai import OpenAI


class AIEngine:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.model = model

    def is_available(self) -> bool:
        return self.client is not None

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
    ):
        def task():
            try:
                if not self.client:
                    on_error(self._friendly_error())
                    return

                res = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.4,
                    max_tokens=900,
                )
                on_complete(res.choices[0].message.content.strip())
            except Exception as exc:
                on_error(self._friendly_error(exc))

        threading.Thread(target=task, daemon=True).start()
