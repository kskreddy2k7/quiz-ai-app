from __future__ import annotations

import datetime
import os
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

        kv_path = os.path.join(os.path.dirname(__file__), "app.kv")
        try:
            return Builder.load_file(kv_path)
        except Exception:
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
        home = self.root.get_screen("home")
        home.permission_status = (
            "We will request storage, camera, and microphone access next."
        )
        Clock.schedule_once(self._request_android_permissions, 0.8)

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
            Permission.CAMERA,
            Permission.RECORD_AUDIO,
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
#:import dp kivy.metrics.dp

<PrimaryButton@Button>:
    background_normal: ""
    background_color: 0.25, 0.45, 0.85, 1
    color: 1, 1, 1, 1
    font_size: "16sp"
    size_hint_y: None
    height: dp(48)

<Card@BoxLayout>:
    orientation: "vertical"
    padding: dp(16)
    spacing: dp(12)
    size_hint_y: None
    height: self.minimum_height
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [18, 18, 18, 18]

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
        padding: dp(28)
        spacing: dp(18)
        canvas.before:
            Color:
                rgba: 0.92, 0.95, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Widget:
        Label:
            text: "Quiz AI"
            font_size: "32sp"
            bold: True
            color: 0.15, 0.25, 0.5, 1
        Label:
            text: "Believe in yourself. Small steps every day lead to big success."
            font_size: "18sp"
            color: 0.25, 0.3, 0.45, 1
            text_size: self.width, None
            halign: "center"
            valign: "middle"
        Label:
            text: "Created with motivation by\\nKata Sai Kranthu Reddy"
            font_size: "16sp"
            color: 0.3, 0.35, 0.5, 1
            text_size: self.width, None
            halign: "center"
            valign: "middle"
        Widget:

<HomeScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(16)
        canvas.before:
            Color:
                rgba: 0.95, 0.96, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "Welcome, Learner!"
            font_size: "24sp"
            bold: True
            color: 0.15, 0.2, 0.4, 1
        Label:
            text: root.daily_quote
            font_size: "16sp"
            color: 0.25, 0.3, 0.45, 1
            text_size: self.width, None
            halign: "center"
        Card:
            Label:
                text: "Permission note"
                font_size: "16sp"
                bold: True
                color: 0.2, 0.25, 0.4, 1
            Label:
                text: "We use storage permission to keep study materials offline. Camera and microphone are optional for future learning features."
                font_size: "14sp"
                color: 0.3, 0.35, 0.5, 1
                text_size: self.width, None
                halign: "center"
            Label:
                text: root.permission_status
                font_size: "14sp"
                color: 0.3, 0.35, 0.5, 1
                text_size: self.width, None
                halign: "center"
        PrimaryButton:
            text: "Start Quiz"
            on_release: app.start_quiz()
        PrimaryButton:
            text: "Study Materials"
            on_release: app.root.current = "materials"
        Widget:

<QuizScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: root.progress_text
            font_size: "14sp"
            color: 0.3, 0.35, 0.45, 1
        Label:
            text: root.question_text
            font_size: "20sp"
            bold: True
            color: 0.2, 0.25, 0.4, 1
            text_size: self.width, None
            halign: "center"
        PrimaryButton:
            text: root.option_texts[0] if len(root.option_texts) > 0 else ""
            on_release: app.submit_answer(self.text)
        PrimaryButton:
            text: root.option_texts[1] if len(root.option_texts) > 1 else ""
            on_release: app.submit_answer(self.text)
        PrimaryButton:
            text: root.option_texts[2] if len(root.option_texts) > 2 else ""
            on_release: app.submit_answer(self.text)
        PrimaryButton:
            text: root.option_texts[3] if len(root.option_texts) > 3 else ""
            on_release: app.submit_answer(self.text)
        Button:
            text: "Back to Home"
            size_hint_y: None
            height: dp(44)
            background_normal: ""
            background_color: 0.75, 0.8, 0.9, 1
            color: 0.2, 0.25, 0.4, 1
            on_release: app.go_home()

<ResultsScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(24)
        spacing: dp(16)
        canvas.before:
            Color:
                rgba: 0.95, 0.98, 0.97, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "Quiz Complete!"
            font_size: "22sp"
            bold: True
            color: 0.15, 0.45, 0.35, 1
        Label:
            text: root.score_text
            font_size: "18sp"
            color: 0.2, 0.3, 0.4, 1
        Label:
            text: root.encouragement_text
            font_size: "16sp"
            color: 0.2, 0.3, 0.4, 1
            text_size: self.width, None
            halign: "center"
        PrimaryButton:
            text: "Try Another Quiz"
            on_release: app.start_quiz()
        PrimaryButton:
            text: "Back to Home"
            on_release: app.go_home()

<MaterialsScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: 0.96, 0.97, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "Study Materials"
            font_size: "22sp"
            bold: True
            color: 0.2, 0.25, 0.45, 1
        Label:
            text: "Keep your notes and files handy for quick review."
            font_size: "16sp"
            color: 0.3, 0.35, 0.5, 1
            text_size: self.width, None
            halign: "center"
        Label:
            text: "Store PDFs, PPTs, or DOCs on your device and open them anytime."
            font_size: "14sp"
            color: 0.35, 0.4, 0.55, 1
            text_size: self.width, None
            halign: "center"
        Button:
            text: "Back to Home"
            size_hint_y: None
            height: dp(44)
            background_normal: ""
            background_color: 0.75, 0.8, 0.9, 1
            color: 0.2, 0.25, 0.4, 1
            on_release: app.go_home()
"""


if __name__ == "__main__":
    QuizApp().run()
