from __future__ import annotations

from kivy.properties import NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen


class ProgressScreen(Screen):
    average_score = NumericProperty(0)
    streak_text = StringProperty("")
    history_text = StringProperty("")
