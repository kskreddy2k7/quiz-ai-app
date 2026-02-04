from __future__ import annotations

from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen


class AIChatScreen(Screen):
    chat_history = StringProperty("")
    status_text = StringProperty("")
