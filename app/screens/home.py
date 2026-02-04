from __future__ import annotations

from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen


class HomeScreen(Screen):
    daily_quote = StringProperty("")
    motivation_status = StringProperty("Tap for daily motivation.")
    permission_status = StringProperty("")
    streak_text = StringProperty("Streak: 0 days")
