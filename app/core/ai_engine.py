from __future__ import annotations

import os
import threading
from typing import Callable

from dotenv import load_dotenv
from openai import OpenAI


# Load .env file ONCE
load_dotenv()


class AIEngine:
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = model
        self.client = None

        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def is_available(self) -> bool:
        return self.client is not None

    def _complete(self, prompt: str, system_prompt: str) -> str:
        if not self.client:
            raise RuntimeError("AI not configured. Missing API key.")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=650,
        )

        return response.choices[0].message.content.strip()

    def run_async(
        self,
        prompt: str,
        system_prompt: str,
        on_complete: Callable[[str], None],
        on_error: Callable[[str], None],
    ) -> None:
        def task():
            try:
                text = self._complete(prompt, system_prompt)
                on_complete(text)
            except Exception as e:
                on_error(str(e))

        threading.Thread(target=task, daemon=True).start()
