from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen


class HomeScreen(Screen):
    daily_quote = StringProperty("")
    permission_status = StringProperty("")
    motivation_status = StringProperty("")
    streak_text = StringProperty("Streak: 0 days")
    topic_text = StringProperty("Science")
    difficulty_text = StringProperty("easy")
