from __future__ import annotations

import os
from typing import Callable

import requests

from app.core.utils import run_in_thread


class AIEngine:
    def __init__(self, api_key: str | None = None, model: str = "gpt-3.5-turbo") -> None:
        self.api_key = (api_key or os.getenv("OPENAI_API_KEY", "")).strip()
        self.model = model

    def is_available(self) -> bool:
        return bool(self.api_key)

    def _complete(self, prompt: str, system_prompt: str) -> str:
        if not self.is_available():
            raise ValueError("AI features unavailable. Configure API key.")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
            "max_tokens": 650,
        }
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        if response.status_code != 200:
            raise RuntimeError("AI request failed. Please try again later.")
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    def run_async(
        self,
        prompt: str,
        system_prompt: str,
        on_complete: Callable[[str], None],
        on_error: Callable[[str], None],
    ) -> None:
        def task() -> str:
            return self._complete(prompt, system_prompt)

        run_in_thread(task, on_complete, on_error)
