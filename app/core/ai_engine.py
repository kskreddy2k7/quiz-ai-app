from __future__ import annotations

import os
import threading
from typing import Callable
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class AIEngine:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.model = model

    def is_available(self) -> bool:
        return self.client is not None

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
                    raise RuntimeError("AI not configured")

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
            except Exception as e:
                on_error(str(e))

        threading.Thread(target=task, daemon=True).start()
