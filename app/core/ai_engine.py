from __future__ import annotations

import os
import threading
from typing import Callable, Optional

import requests

OPENAI_URL = "https://api.openai.com/v1/chat/completions"


class AIEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def run_async(
        self,
        prompt: str,
        system_prompt: str,
        on_complete: Callable[[str], None],
        on_error: Callable[[str], None],
        timeout: int = 15,
    ) -> None:
        thread = threading.Thread(
            target=self._request,
            args=(prompt, system_prompt, on_complete, on_error, timeout),
            daemon=True,
        )
        thread.start()

    def _request(
        self,
        prompt: str,
        system_prompt: str,
        on_complete: Callable[[str], None],
        on_error: Callable[[str], None],
        timeout: int,
    ) -> None:
        if not self.api_key:
            on_error("AI features unavailable. Configure API key.")
            return
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.6,
                "max_tokens": 200,
            }
            response = requests.post(OPENAI_URL, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            on_complete(content)
        except Exception:
            on_error("AI is taking a break. Please try again soon.")
