from kivy.properties import BooleanProperty, ListProperty, StringProperty
from kivy.uix.screenmanager import Screen


class QuizScreen(Screen):
    question_text = StringProperty("")
    option_texts = ListProperty([])
    progress_text = StringProperty("")
    explanation_text = StringProperty("")
    show_next = BooleanProperty(False)
