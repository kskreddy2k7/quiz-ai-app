from __future__ import annotations

import datetime
from typing import Callable, List

from app.core.ai_engine import AIEngine


LOCAL_QUOTES = [
    "Believe in yourself. Small steps every day lead to big success.",
    "You are capable of amazing progress. Keep going.",
    "Small wins add up. Celebrate your effort today.",
]


class MotivationEngine:
    def __init__(self, ai_engine: AIEngine):
        self.ai_engine = ai_engine

    def get_daily_quote(self) -> str:
        index = datetime.date.today().toordinal() % len(LOCAL_QUOTES)
        return LOCAL_QUOTES[index]

    def request_ai_motivation(self, on_complete: Callable[[str], None], on_error: Callable[[str], None]) -> None:
        prompt = "Write one short motivational sentence for a student studying today."
        system_prompt = "You are a supportive student coach."
        self.ai_engine.run_async(prompt, system_prompt, on_complete, on_error)
