from __future__ import annotations

import datetime
import os
import random
from typing import Optional
from dataclasses import dataclass
from typing import List

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.utils import platform


@dataclass(frozen=True)
class Question:
    prompt: str
    choices: List[str]
    answer: str


QUESTIONS = [
    Question(
        prompt="What is the powerhouse of the cell?",
        choices=["Nucleus", "Mitochondria", "Ribosome", "Golgi body"],
        answer="Mitochondria",
    ),
    Question(
        prompt="Which planet is known as the Red Planet?",
        choices=["Venus", "Saturn", "Mars", "Jupiter"],
        answer="Mars",
    ),
    Question(
        prompt="What is 9 × 7?",
        choices=["56", "63", "72", "79"],
        answer="63",
    ),
    Question(
        prompt="Which language is primarily used for Android development?",
        choices=["Kotlin", "Swift", "Ruby", "Go"],
        answer="Kotlin",
    ),
    Question(
        prompt="What gas do plants absorb from the atmosphere?",
        choices=["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"],
        answer="Carbon Dioxide",
    ),
    Question(
        prompt="Who wrote 'Romeo and Juliet'?",
        choices=["William Shakespeare", "Jane Austen", "Mark Twain", "Leo Tolstoy"],
        answer="William Shakespeare",
    ),
    Question(
        prompt="Which organ pumps blood throughout the body?",
        choices=["Lungs", "Heart", "Liver", "Kidney"],
        answer="Heart",
    ),
    Question(
        prompt="What is the boiling point of water in Celsius?",
        choices=["90°C", "100°C", "110°C", "120°C"],
        answer="100°C",
    ),
]

MOTIVATIONAL_QUOTES = [
    "Believe in yourself. Every great achievement starts with a small step.",
    "Small progress every day leads to big results.",
    "Learning is a journey—enjoy each step and keep going.",
    "Consistency beats intensity. Show up and grow.",
    "Your future self will thank you for studying today.",
    "Every question you try makes you stronger and smarter.",
]

ENCOURAGEMENTS = [
    "Great effort! Keep building your confidence with every quiz.",
    "Well done! You are learning more every day.",
    "Fantastic work! Your dedication is inspiring.",
    "Awesome! Keep up the steady momentum.",
]


class SplashScreen(Screen):
    pass


class HomeScreen(Screen):
    daily_quote = StringProperty("")
    permission_status = StringProperty("Preparing to request permissions...")


class QuizScreen(Screen):
    question_text = StringProperty("")
    option_texts = ListProperty([])
    progress_text = StringProperty("")


class ResultsScreen(Screen):
    score_text = StringProperty("")
    encouragement_text = StringProperty("")


class MaterialsScreen(Screen):
    pass


class QuizApp(App):
    title = "Quiz AI"

    current_index = NumericProperty(0)
    score = NumericProperty(0)
    active_questions: List[Question]
    last_screen: Optional[str] = None

    def build(self):
        self.active_questions = []
        Window.bind(on_keyboard=self._handle_back)
        if os.path.exists("app.kv"):
            return Builder.load_file("app.kv")
        return Builder.load_string(
            """
<PrimaryLabel@Label>:
    color: 0.1, 0.1, 0.15, 1
    font_size: "18sp"
    text_size: self.width, None
    halign: "center"
    valign: "middle"

ScreenManager:
    SplashScreen:
        name: "splash"
    HomeScreen:
        name: "home"

<SplashScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: "24dp"
        spacing: "20dp"
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
            color: 0.1, 0.2, 0.4, 1
        Label:
            text: "Believe in yourself. Small steps every day lead to big success."
            font_size: "18sp"
            color: 0.2, 0.2, 0.3, 1
            text_size: self.width, None
            halign: "center"
        Label:
            text: "Created with motivation by\\nKata Sai Kranthu Reddy"
            font_size: "16sp"
            color: 0.25, 0.25, 0.35, 1
            text_size: self.width, None
            halign: "center"
        Widget:

<HomeScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "16dp"
        canvas.before:
            Color:
                rgba: 0.98, 0.98, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "Welcome, Learner!"
            font_size: "26sp"
            bold: True
            color: 0.15, 0.2, 0.35, 1
        PrimaryLabel:
            text: root.daily_quote
        Widget:
        """
        )

    def on_start(self):
        self._refresh_daily_quote()
        self.generate_quiz()
        self._show_home_after_splash()

    def _show_home_after_splash(self):
        Clock.schedule_once(self._go_home_from_splash, 2)

    def _go_home_from_splash(self, _dt):
        if self.root:
            self.root.current = "home"
            Clock.schedule_once(self._request_android_permissions, 0.5)

    def _request_android_permissions(self, _dt):
        if platform != "android":
            return
        from android.permissions import Permission, request_permissions

        permissions = [
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ]
        home_screen = self.root.get_screen("home")
        home_screen.permission_status = "Requesting permissions..."
        request_permissions(permissions, self._on_permissions_result)

    def _on_permissions_result(self, permissions, grants):
        if not self.root:
            return
        denied = [
            permission
            for permission, granted in zip(permissions, grants)
            if not granted
        ]
        home_screen = self.root.get_screen("home")
        if denied:
            home_screen.permission_status = (
                "Some permissions were denied. You can still study, "
                "but saving materials or using media features may be limited."
            )
        else:
            home_screen.permission_status = "All requested permissions were granted."

    def _handle_back(self, _window, key, *_args):
        if key != 27:
            return False
        current = self.root.current
        if current in {"quiz", "results", "materials"}:
            self.go_home()
            return True
        return False

    def _refresh_daily_quote(self):
        today_index = datetime.date.today().toordinal() % len(MOTIVATIONAL_QUOTES)
        quote = MOTIVATIONAL_QUOTES[today_index]
        home_screen = self.root.get_screen("home")
        home_screen.daily_quote = quote

    def generate_quiz(self):
        self.active_questions = random.sample(QUESTIONS, k=min(5, len(QUESTIONS)))
        self.current_index = 0
        self.score = 0
        self._load_question()

    def _load_question(self):
        if self.current_index >= len(self.active_questions):
            self.show_results()
            return
        question = self.active_questions[self.current_index]
        quiz_screen = self.root.get_screen("quiz")
        quiz_screen.question_text = question.prompt
        quiz_screen.option_texts = list(question.choices)
        quiz_screen.progress_text = (
            f"Question {self.current_index + 1} of {len(self.active_questions)}"
        )

    def submit_answer(self, answer: str):
        if not self.active_questions or self.current_index >= len(self.active_questions):
            return
        question = self.active_questions[self.current_index]
        if answer == question.answer:
            self.score += 1
        self.current_index += 1
        self._load_question()

    def show_results(self):
        results_screen = self.root.get_screen("results")
        total = len(self.active_questions)
        percent = int((self.score / total) * 100) if total else 0
        results_screen.score_text = (
            f"You scored {self.score} out of {total} ({percent}%)."
        )
        encouragement_index = min(percent // 25, len(ENCOURAGEMENTS) - 1)
        results_screen.encouragement_text = ENCOURAGEMENTS[encouragement_index]
        self.root.current = "results"

    def restart_quiz(self):
        self.generate_quiz()
        self.root.current = "quiz"

    def go_home(self):
        self._refresh_daily_quote()
        self.root.current = "home"


if __name__ == "__main__":
    QuizApp().run()
