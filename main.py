from __future__ import annotations

import datetime
from pathlib import Path
from typing import List

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import ScreenManager

from app.core.ai_engine import AIEngine
from app.core.doubt_solver import DoubtSolver
from app.core.explanation_engine import ExplanationEngine
from app.core.permission_manager import PermissionManager
from app.core.quiz_generator import QuizGenerator, QuizQuestion
from app.core.storage import StorageManager
from app.core.utils import build_daily_quote

from app.screens.ai_chat import AIChatScreen
from app.screens.explanation import ExplanationScreen
from app.screens.home import HomeScreen
from app.screens.materials import MaterialsScreen
from app.screens.progress import ProgressScreen
from app.screens.quiz_play import QuizPlayScreen
from app.screens.quiz_setup import QuizSetupScreen
from app.screens.results import ResultsScreen
from app.screens.splash import SplashScreen


ENCOURAGEMENTS = [
    "🌟 Great effort! Keep going!",
    "🔥 Well done! You're improving!",
    "🚀 Fantastic work! Stay consistent!",
]


class QuizAIApp(App):
    title = "Quiz AI"

    current_index = NumericProperty(0)
    score = NumericProperty(0)

    active_questions: List[QuizQuestion]
    last_topic: str = "General"
    current_difficulty: str = "easy"
    last_explanation: str = ""
    last_selected_answer: str = ""

    # -------------------------
    # APP STARTUP
    # -------------------------

    def build(self):
        self.active_questions = []

        # AI CORE
        self.ai_engine = AIEngine()
        self.doubt_solver = DoubtSolver(self.ai_engine)
        self.quiz_generator = QuizGenerator(
            self.ai_engine, self._data_path("local_questions.json")
        )
        self.explanation_engine = ExplanationEngine(self.ai_engine)

        # SYSTEM
        self.permission_manager = PermissionManager()
        self.storage = StorageManager(Path(self.user_data_dir) / "quiz_data.json")

        self._load_kv_files()

        manager = ScreenManager()
        manager.add_widget(SplashScreen(name="splash"))
        manager.add_widget(HomeScreen(name="home"))
        manager.add_widget(AIChatScreen(name="ai_chat"))
        manager.add_widget(QuizSetupScreen(name="quiz_setup"))
        manager.add_widget(QuizPlayScreen(name="quiz_play"))
        manager.add_widget(ExplanationScreen(name="explanation"))
        manager.add_widget(ResultsScreen(name="results"))
        manager.add_widget(MaterialsScreen(name="materials"))
        manager.add_widget(ProgressScreen(name="progress"))

        return manager

    def _data_path(self, filename: str) -> Path:
        return Path(__file__).resolve().parent / "data" / filename

    def _load_kv_files(self) -> None:
        ui_dir = Path(__file__).resolve().parent / "app" / "ui"
        for file in [
            "splash.kv",
            "home.kv",
            "ai_chat.kv",
            "quiz_setup.kv",
            "quiz_play.kv",
            "explanation.kv",
            "results.kv",
            "materials.kv",
            "progress.kv",
        ]:
            Builder.load_file(str(ui_dir / file))

    def on_start(self):
        self._refresh_daily_quote()
        Clock.schedule_once(self._go_home_from_splash, 1.5)

    # -------------------------
    # NAVIGATION
    # -------------------------

    def _go_home_from_splash(self, _dt):
        self.root.current = "home"
        Clock.schedule_once(self._request_permissions, 0.5)

    def go_home(self):
        self._refresh_daily_quote()
        self.root.current = "home"

    def go_ai_chat(self):
        screen = self.root.get_screen("ai_chat")
        screen.status_text = ""
        self.root.current = "ai_chat"

    def go_quiz_setup(self):
        screen = self.root.get_screen("quiz_setup")
        screen.load_subjects(self._data_path("subjects.json"))
        self.root.current = "quiz_setup"

    def go_progress(self):
        self._refresh_progress()
        self.root.current = "progress"

    def go_materials(self):
        self._refresh_materials()
        self.root.current = "materials"

    # -------------------------
    # PERMISSIONS
    # -------------------------

    def _request_permissions(self, _dt):
        home = self.root.get_screen("home")
        home.permission_status = "Requesting permissions…"

        def update(msg: str):
            home.permission_status = msg

        self.permission_manager.request_permissions(update)

    # -------------------------
    # QUIZ FLOW
    # -------------------------

    def start_quiz(self, subject: str, topic: str, difficulty: str):
        self.last_topic = f"{subject} · {topic}" if topic else subject
        self.current_difficulty = difficulty or "easy"
        self.root.current = "quiz_play"

        quiz = self.root.get_screen("quiz_play")
        quiz.question_text = "🧠 Preparing your quiz..."
        quiz.option_texts = []
        quiz.progress_text = ""

        def on_complete(questions: List[QuizQuestion]):
            self._start_questions(questions)

        def on_error(_msg: str):
            questions = self.quiz_generator.get_local_quiz(
                subject, topic, self.current_difficulty
            )
            self._start_questions(questions)

        if self.ai_engine.is_available():
            quiz.progress_text = "✨ Generating AI quiz..."
            self.quiz_generator.request_ai_quiz(
                subject, topic, self.current_difficulty, on_complete, on_error
            )
        else:
            on_error("offline")

    def _start_questions(self, questions: List[QuizQuestion]):
        if not questions:
            quiz = self.root.get_screen("quiz_play")
            quiz.question_text = "No questions available."
            quiz.option_texts = []
            return

        self.active_questions = questions
        self.current_index = 0
        self.score = 0
        self._load_question()

    def _load_question(self):
        if self.current_index >= len(self.active_questions):
            self.show_results()
            return

        q = self.active_questions[self.current_index]
        quiz = self.root.get_screen("quiz_play")
        quiz.question_text = q.prompt
        quiz.option_texts = q.choices
        quiz.progress_text = f"{self.current_index + 1}/{len(self.active_questions)}"

    def submit_answer(self, answer: str):
        q = self.active_questions[self.current_index]
        self.last_selected_answer = answer

        if answer == q.answer:
            self.score += 1

        explanation = self.root.get_screen("explanation")
        explanation.result_text = "✅ Correct!" if answer == q.answer else "❌ Not quite"
        explanation.explanation_text = "Thinking..."
        explanation.selected_answer = answer
        explanation.correct_answer = q.answer
        explanation.next_label = (
            "Next" if self.current_index + 1 < len(self.active_questions) else "Results"
        )
        self.root.current = "explanation"

        def on_complete(text: str):
            explanation.explanation_text = text
            self.last_explanation = text

        def on_error(_msg: str):
            fallback = self.explanation_engine.fallback_explanation(q, answer)
            explanation.explanation_text = fallback
            self.last_explanation = fallback

        self.explanation_engine.request_explanation(q, answer, on_complete, on_error)

    def next_question(self):
        self.current_index += 1
        self._load_question()
        self.root.current = "quiz_play"

    def show_results(self):
        results = self.root.get_screen("results")
        total = len(self.active_questions)
        percent = int((self.score / total) * 100) if total else 0

        results.score_text = f"Score: {self.score}/{total} ({percent}%)"
        results.encouragement_text = ENCOURAGEMENTS[min(percent // 34, 2)]
        results.explanation_text = self.last_explanation

        self._store_results(percent)
        self.root.current = "results"

    def _store_results(self, percent: int):
        today = datetime.date.today().isoformat()
        streak = self.storage.update_streak(today)

        self.storage.add_history(
            {
                "date": today,
                "topic": self.last_topic,
                "difficulty": self.current_difficulty,
                "score": percent,
            }
        )

        self.storage.update_score(percent)
        home = self.root.get_screen("home")
        home.streak_text = f"Streak: {streak} days"

    # -------------------------
    # AI CHAT
    # -------------------------

    def send_ai_question(self, question: str):
        screen = self.root.get_screen("ai_chat")
        question = question.strip()

        if not question:
            screen.status_text = "Please enter a question."
            return

        screen.status_text = "Tutor is thinking…"
        screen.chat_history += f"\nYou: {question}\n"

        def on_complete(text: str):
            screen.chat_history += f"Tutor: {text}\n"
            screen.status_text = ""

        def on_error(msg: str):
            screen.chat_history += f"Tutor: {msg}\n"
            screen.status_text = ""

        self.doubt_solver.solve(question, on_complete, on_error)

    # -------------------------
    # MATERIALS
    # -------------------------

    def add_material_entry(self, label: str, path: str):
        self.storage.add_material({"label": label, "path": path})
        self._refresh_materials()

    def _refresh_materials(self):
        screen = self.root.get_screen("materials")
        items = self.storage.get_materials()
        screen.materials_text = (
            "\n".join(f"• {i['label']}" for i in items)
            if items
            else "No materials saved yet."
        )

    # -------------------------
    # PROGRESS
    # -------------------------

    def _refresh_progress(self):
        data = self.storage.load()
        scores = data.get("scores", [])
        avg = int(sum(scores) / len(scores)) if scores else 0

        history = data.get("history", [])
        lines = [
            f"{i['date']} · {i['topic']} · {i['score']}%" for i in history
        ]

        screen = self.root.get_screen("progress")
        screen.average_score = avg
        screen.streak_text = f"Streak: {data.get('streak', 0)} days"
        screen.history_text = "\n".join(lines) if lines else "No quizzes yet."

    # -------------------------
    # DAILY MOTIVATION
    # -------------------------

    def _refresh_daily_quote(self):
        home = self.root.get_screen("home")
        home.daily_quote = build_daily_quote()

    def request_daily_motivation(self):
        home = self.root.get_screen("home")
        home.motivation_status = "✨ Loading motivation..."

        def on_complete(text: str):
            home.motivation_status = text

        def on_error(_msg: str):
            home.motivation_status = "📴 Offline: Keep learning every day!"

        if self.ai_engine.is_available():
            self.ai_engine.run_async(
                "Give a short study motivation with emojis.",
                "You are a motivating tutor.",
                on_complete,
                on_error,
            )
        else:
            on_error("offline")


if __name__ == "__main__":
    QuizAIApp().run()
