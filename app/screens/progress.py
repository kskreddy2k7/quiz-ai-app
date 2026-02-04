from kivy.properties import NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen


class ProgressScreen(Screen):
    average_score = NumericProperty(0)
    streak_text = StringProperty("Streak: 0 days")
    history_text = StringProperty("No quizzes yet.")
