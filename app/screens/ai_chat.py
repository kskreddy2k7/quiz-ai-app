from __future__ import annotations

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import Screen

from app.ui.theme import Theme


class ChatBubble(BoxLayout):
    text = StringProperty("")
    is_user = BooleanProperty(True)
    bg_color = ListProperty([0, 0, 0, 0])
    text_color = ListProperty([1, 1, 1, 1])

    def on_is_user(self, instance, value):
        if value:
            # User Bubble: Accent/Primary Gradientish
            self.bg_color = Theme.color(Theme.PRIMARY, 0.2)
            self.text_color = Theme.color(Theme.TEXT_PRIMARY)
            self.pos_hint = {"right": 1}
        else:
            # AI Bubble: Card Background
            self.bg_color = Theme.color(Theme.BG_CARD, 0.4)
            self.text_color = Theme.color(Theme.TEXT_SECONDARY)
            self.pos_hint = {"x": 0}


class ChatRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []


class AIChatScreen(Screen):
    status_text = StringProperty("")
    is_loading = BooleanProperty(False)

    def on_enter(self):
        # Refresh API status when entering
        app = App.get_running_app()
        if not app.ai_service.is_available():
            self.status_text = "⚠️ AI is offline (API Key Missing)"
        else:
            self.status_text = ""

    def send_message(self, text: str):
        text = text.strip()
        if not text:
            return

        app = App.get_running_app()
        if not app.ai_service.is_available():
            self.status_text = "Please add API Key in settings first."
            return

        # Add User Message
        self.add_message(text, is_user=True)
        self.is_loading = True
        self.status_text = "Identifying concepts..."

        # Call Service
        app.tutor_service.solve_doubt(
            text,
            on_complete=self.on_ai_response,
            on_error=self.on_ai_error
        )

    def on_ai_response(self, text: str):
        self.is_loading = False
        self.status_text = ""
        self.add_message(text, is_user=False)

    def on_ai_error(self, error: str):
        self.is_loading = False
        self.status_text = ""
        self.add_message(f"Error: {error}", is_user=False)

    def add_message(self, text: str, is_user: bool):
        rv = self.ids.chat_list
        rv.data.append({
            "text": text,
            "is_user": is_user
        })
        # Scroll to bottom
        Clock.schedule_once(lambda dt: self.scroll_to_bottom(), 0.1)

    def scroll_to_bottom(self):
        rv = self.ids.chat_list
        if rv.data:
            rv.scroll_y = 0
