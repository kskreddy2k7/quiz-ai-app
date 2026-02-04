from __future__ import annotations

import os
from typing import Callable

from openai import OpenAI, OpenAIError

from app.utils.helpers import run_in_thread


class AIService:
    """
    Central service for interacting with OpenAI.
    Handles API keys, client initialization, and error formatting.
    """
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = None
        self.api_key = None
        self._refresh_client()

    def _refresh_client(self) -> None:
        # Prioritize env var, could extend to load from local storage if needed
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def set_api_key(self, key: str) -> None:
        """Allow setting API key at runtime (e.g. from UI input)"""
        os.environ["OPENAI_API_KEY"] = key
        self._refresh_client()

    def is_available(self) -> bool:
        self._refresh_client()
        return self.client is not None

    def availability_message(self) -> str:
        self._refresh_client()
        if not self.api_key:
            return "AI Mode: Offline 📴 (Missing API Key)"
        return "AI Mode: Online ✨"

    def _friendly_error(self, exc: Exception | None = None) -> str:
        if not self.api_key:
            return "📴 AI is offline. Please enter your API key in settings."
        
        message = str(exc).lower() if exc else ""
        if "connection" in message or "timeout" in message:
            return "📴 Network error. Check your internet."
        if "quota" in message:
            return "⚠️ AI quota exceeded. Check your OpenAI plan."
        if "rate limit" in message:
            return "⏳ Too many requests. Please wait a moment."
            
        print(f"DEBUG: AI Error: {exc}") # Log for dev
        return "🤖 AI service unavailable. Try again later."

    def run_async(
        self,
        prompt: str,
        system_prompt: str,
        on_complete: Callable[[str], None],
        on_error: Callable[[str], None],
        temperature: float = 0.7
    ) -> None:
        self._refresh_client()

        def task() -> str:
            if not self.client:
                raise RuntimeError("No API key provided")

            try:
                res = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=1000,
                )
                return res.choices[0].message.content.strip()
            except OpenAIError as e:
                raise e

        run_in_thread(
            task,
            on_complete,
            lambda message: on_error(self._friendly_error(Exception(message))),
        )
