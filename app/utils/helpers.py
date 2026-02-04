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
    "Learning is a treasure that will follow its owner everywhere.",
    "The beautiful thing about learning is that no one can take it away from you.",
]


def run_in_thread(task: Callable[[], T], on_complete: Callable[[T], None], on_error: Callable[[str], None]) -> None:
    """
    Runs a blocking task in a separate thread to prevent UI freezing.
    Callbacks are scheduled on the main Kivy thread.
    """
    def wrapper() -> None:
        try:
            result = task()
        except Exception as exc:
            # Capture error message immediately as 'exc' is deleted after except block
            error_msg = str(exc)
            Clock.schedule_once(lambda _dt: on_error(error_msg), 0)
        else:
            Clock.schedule_once(lambda _dt: on_complete(result), 0)

    Thread(target=wrapper, daemon=True).start()


def build_daily_quote() -> str:
    return random.choice(DAILY_QUOTES)
