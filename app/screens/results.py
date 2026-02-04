from __future__ import annotations

from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen


class ResultsScreen(Screen):
    score_text = StringProperty("")
    encouragement_text = StringProperty("")
    explanation_text = StringProperty("")
