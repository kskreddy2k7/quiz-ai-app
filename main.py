from __future__ import annotations

import datetime
import random
from dataclasses import dataclass
from typing import List, Optional

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.utils import platform

# Window import MUST be safe
try:
    from kivy.core.window import Window
except Exception:
    Window = None


# =========================
# DATA MODELS
# =========================

@dataclass(frozen=True)
class Question:
    prompt: str
    choices: List[str]
    answer: str


QUESTIONS = [
    Question("What is the powerhouse of the cell?",
             ["Nucleus", "Mitochondria", "Ribosome", "Golgi body"], "Mitochondria"),
    Question("Which planet is known as the Red Planet?",
             ["Venus", "Saturn", "Mars", "Jupiter"], "Mars"),
    Question("What is 9 × 7?",
             ["56", "63", "72", "79"], "63"),
    Question("Which language is primarily used for Android development?",
             ["Kotlin", "Swift", "Ruby", "Go"], "Kotlin"),
]

MOTIVATIONAL_QUOTES = [
    "Believe in yourself. Small steps every day lead to big success.",
    "Consistency beats intensity. Keep learning.",
    "Your future self will thank you for studying today.",
]

ENCOURAGEMENTS = [
    "Great effort! Keep going.",
    "Well done! You're improving.",
    "Fantastic work! Stay consistent.",
]


# =========================
# SCREENS
# =========================

class SplashScreen(Screen):
    pass


class HomeScreen(Screen):
    daily_quote = StringProperty("")
    permission_status = StringProperty("")


class QuizScreen(Screen):
    question_text = StringProperty("")
    option_texts = ListProperty([])
    progress_text = StringProperty("")


class ResultsScreen(Screen):
    score_text = StringProperty("")
    encouragement_text = StringProperty("")


class MaterialsScreen(Screen):
    pass


# =========================
# APP
# =========================

class QuizApp(App):
    title = "Quiz AI"

    current_index = NumericProperty(0)
    score = NumericProperty(0)

    active_questions: List[Question]
    last_screen: Optional[str] = None

    def build(self):
        self.active_questions = []

        # SAFE back button binding
        if Window:
            Window.bind(on_keyboard=self._handle_back)

        return Builder.load_string(self._kv())

    def on_start(self):
        self._refresh_daily_quote()
        Clock.schedule_once(self._go_home_from_splash, 2)

    # -------------------------
    # NAVIGATION
    # -------------------------

    def _go_home_from_splash(self, _dt):
        if not self.root:
            return
        self.root.current = "home"
        Clock.schedule_once(self._request_android_permissions, 0.5)

    def go_home(self):
        self._refresh_daily_quote()
        self.root.current = "home"

    # -------------------------
    # PERMISSIONS (SAFE)
    # -------------------------

    def _request_android_permissions(self, _dt):
        if platform != "android":
            return

        try:
            from android.permissions import Permission, request_permissions
        except Exception:
            return

        permissions = [
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ]

        home = self.root.get_screen("home")
        home.permission_status = "Requesting permissions…"

        request_permissions(permissions, self._on_permissions_result)

    def _on_permissions_result(self, permissions, grants):
        if not self.root:
            return

        home = self.root.get_screen("home")
        if all(grants):
            home.permission_status = "Permissions granted."
        else:
            home.permission_status = "Some permissions denied."

    # -------------------------
    # QUIZ LOGIC
    # -------------------------

    def start_quiz(self):
        self.active_questions = random.sample(
            QUESTIONS, k=min(3, len(QUESTIONS))
        )
        self.current_index = 0
        self.score = 0
        self._load_question()
        self.root.current = "quiz"

    def _load_question(self):
        if self.current_index >= len(self.active_questions):
            self.show_results()
            return

        q = self.active_questions[self.current_index]
        quiz = self.root.get_screen("quiz")
        quiz.question_text = q.prompt
        quiz.option_texts = q.choices
        quiz.progress_text = f"{self.current_index + 1}/{len(self.active_questions)}"

    def submit_answer(self, answer):
        q = self.active_questions[self.current_index]
        if answer == q.answer:
            self.score += 1
        self.current_index += 1
        self._load_question()

    def show_results(self):
        results = self.root.get_screen("results")
        total = len(self.active_questions)
        percent = int((self.score / total) * 100)
        results.score_text = f"Score: {self.score}/{total} ({percent}%)"
        results.encouragement_text = ENCOURAGEMENTS[min(percent // 34, 2)]
        self.root.current = "results"

    # -------------------------
    # BACK BUTTON
    # -------------------------

    def _handle_back(self, _window, key, *_args):
        if key == 27:
            self.go_home()
            return True
        return False

    # -------------------------
    # QUOTES
    # -------------------------

    def _refresh_daily_quote(self):
        quote = MOTIVATIONAL_QUOTES[
            datetime.date.today().toordinal() % len(MOTIVATIONAL_QUOTES)
        ]
        self.root.get_screen("home").daily_quote = quote

    # -------------------------
    # KV
    # -------------------------

    def _kv(self):
        return """
ScreenManager:
    SplashScreen:
        name: "splash"
    HomeScreen:
        name: "home"
    QuizScreen:
        name: "quiz"
    ResultsScreen:
        name: "results"
    MaterialsScreen:
        name: "materials"

<SplashScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: "24dp"
        spacing: "20dp"
        Label:
            text: "Believe in yourself. Small steps every day lead to big success."
        Label:
            text: "Created with motivation by\\nKata Sai Kranthu Reddy"

<HomeScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: "20dp"
        Label:
            text: "Welcome!"
            font_size: "24sp"
        Label:
            text: root.daily_quote
        Label:
            text: root.permission_status
        Button:
            text: "Start Quiz"
            on_release: app.start_quiz()

<QuizScreen>:
    BoxLayout:
        orientation: "vertical"
        Label:
            text: root.question_text
        Button:
            text: root.option_texts[0] if root.option_texts else ""
            on_release: app.submit_answer(self.text)
        Button:
            text: root.option_texts[1] if root.option_texts else ""
            on_release: app.submit_answer(self.text)
        Button:
            text: root.option_texts[2] if root.option_texts else ""
            on_release: app.submit_answer(self.text)
        Button:
            text: root.option_texts[3] if root.option_texts else ""
            on_release: app.submit_answer(self.text)

<ResultsScreen>:
    BoxLayout:
        orientation: "vertical"
        Label:
            text: root.score_text
        Label:
            text: root.encouragement_text
        Button:
            text: "Home"
            on_release: app.go_home()
"""


if __name__ == "__main__":
    QuizApp().run()
