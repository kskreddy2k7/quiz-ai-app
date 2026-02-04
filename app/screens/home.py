from __future__ import annotations

from kivy.properties import BooleanProperty, ListProperty, StringProperty
from kivy.uix.screenmanager import Screen


class HomeScreen(Screen):
    daily_quote = StringProperty("")
    motivation_status = StringProperty("Tap for daily motivation.")
    permission_status = StringProperty("")
    streak_text = StringProperty("Streak: 0 days")
    ai_status = StringProperty("AI Mode: Offline")
    ai_status_color = ListProperty([0.8, 0.9, 1, 0.9])
    ai_available = BooleanProperty(False)
