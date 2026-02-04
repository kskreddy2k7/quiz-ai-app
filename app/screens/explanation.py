from __future__ import annotations

from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen


class ExplanationScreen(Screen):
    result_text = StringProperty("")
    explanation_text = StringProperty("")
    selected_answer = StringProperty("")
    correct_answer = StringProperty("")
    next_label = StringProperty("Next")
