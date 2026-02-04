from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen


class AITutorScreen(Screen):
    chat_history = StringProperty("")
    status_text = StringProperty("")
