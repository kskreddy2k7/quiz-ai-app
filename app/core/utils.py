from __future__ import annotations

import random
from threading import Thread
from typing import Callable, TypeVar

from kivy.clock import Clock

T = TypeVar("T")

DAILY_QUOTES = [
    "Small steps every day build unstoppable momentum.",
    "Curiosity is your superpower. Keep asking why.",
    "Progress is progress, even on hard days.",
    "Your future self will thank you for today’s effort.",
]


def run_in_thread(task: Callable[[], T], on_complete: Callable[[T], None], on_error: Callable[[str], None]) -> None:
    def wrapper() -> None:
        try:
            result = task()
        except Exception as exc:
            Clock.schedule_once(lambda _dt: on_error(str(exc)), 0)
        else:
            Clock.schedule_once(lambda _dt: on_complete(result), 0)

    Thread(target=wrapper, daemon=True).start()


def build_daily_quote() -> str:
    return random.choice(DAILY_QUOTES)
