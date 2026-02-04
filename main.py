from __future__ import annotations

import datetime
from pathlib import Path
from typing import List, Optional

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import ScreenManager

from app.core.ai_engine import AIEngine
from app.core.motivation_engine import MotivationEngine
from app.core.permission_manager import PermissionManager
from app.core.quiz_engine import QuizEngine, QuizQuestion
from app.core.storage import StorageManager
from app.screens.ai_tutor import AITutorScreen
from app.screens.home import HomeScreen
from app.screens.materials import MaterialsScreen
from app.screens.progress import ProgressScreen
from app.screens.quiz import QuizScreen
from app.screens.results import ResultsScreen
from app.screens.splash import SplashScreen

# Window import MUST be safe
try:
    from kivy.core.window import Window
except Exception:
    Window = None


ENCOURAGEMENTS = [
    "Great effort! Keep going.",
    "Well done! You're improving.",
    "Fantastic work! Stay consistent.",
]


class QuizAIApp(App):
    title = "Quiz AI"

    current_index = NumericProperty(0)
    score = NumericProperty(0)

    active_questions: List[QuizQuestion]
    last_topic: str = "Science"
    current_difficulty: str = "easy"
    last_explanation: str = ""

    def build(self):
        self.active_questions = []
        self.ai_engine = AIEngine()
        self.motivation_engine = MotivationEngine(self.ai_engine)
        self.permission_manager = PermissionManager()

        data_path = Path(__file__).resolve().parent / "data" / "local_questions.json"
        self.quiz_engine = QuizEngine(data_path, self.ai_engine)

        storage_path = Path(self.user_data_dir) / "quiz_data.json"
        self.storage = StorageManager(storage_path)

        self._load_kv_files()

        manager = ScreenManager()
        manager.add_widget(SplashScreen(name="splash"))
        manager.add_widget(HomeScreen(name="home"))
        manager.add_widget(QuizScreen(name="quiz"))
        manager.add_widget(ResultsScreen(name="results"))
        manager.add_widget(ProgressScreen(name="progress"))
        manager.add_widget(MaterialsScreen(name="materials"))
        manager.add_widget(AITutorScreen(name="ai_tutor"))

        if Window:
            Window.bind(on_keyboard=self._handle_back)

        return manager

    def _load_kv_files(self) -> None:
        ui_dir = Path(__file__).resolve().parent / "app" / "ui"
        for filename in [
            "styles.kv",
            "splash.kv",
            "home.kv",
            "quiz.kv",
            "ai_tutor.kv",
            "results.kv",
            "progress.kv",
            "materials.kv",
        ]:
            Builder.load_file(str(ui_dir / filename))

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
        self._refresh_motivation()
        Clock.schedule_once(self._request_permissions, 0.8)

    def go_home(self):
        self._refresh_daily_quote()
        self.root.current = "home"

    def go_ai_tutor(self):
        screen = self.root.get_screen("ai_tutor")
        screen.status_text = ""
        self.root.current = "ai_tutor"

    def go_progress(self):
        self._refresh_progress()
        self.root.current = "progress"

    def go_materials(self):
        self.root.current = "materials"

    # -------------------------
    # PERMISSIONS
    # -------------------------

    def _request_permissions(self, _dt):
        home = self.root.get_screen("home")
        home.permission_status = "Requesting permissions…"

        def update_status(message: str) -> None:
            home.permission_status = message

        self.permission_manager.request_permissions(update_status)

    # -------------------------
    # QUIZ FLOW
    # -------------------------

    def start_quiz(self, topic: str, difficulty: str):
        self.last_topic = topic.strip() or "General"
        self.current_difficulty = difficulty or self.quiz_engine.difficulty
        self.root.current = "quiz"
        quiz = self.root.get_screen("quiz")
        quiz.question_text = "Preparing your quiz..."
        quiz.option_texts = []
        quiz.progress_text = ""
        quiz.explanation_text = ""
        quiz.show_next = False

        if self.ai_engine.is_available():
            quiz.progress_text = "Generating AI quiz..."
            self.quiz_engine.request_ai_quiz(
                self.last_topic,
                self.current_difficulty,
                self._start_questions,
                lambda message: self._fallback_quiz(quiz, message),
            )
        else:
            self._fallback_quiz(quiz, "AI features unavailable. Using offline questions.")

    def _fallback_quiz(self, quiz: QuizScreen, message: str) -> None:
        quiz.progress_text = message
        questions = self.quiz_engine.get_local_quiz(self.last_topic, self.current_difficulty)
        self._start_questions(questions)

    def _start_questions(self, questions: List[QuizQuestion]):
        if not questions:
            quiz = self.root.get_screen("quiz")
            quiz.question_text = "No questions available yet."
            quiz.option_texts = []
            quiz.progress_text = ""
            quiz.show_next = False
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
        quiz = self.root.get_screen("quiz")
        quiz.question_text = q.prompt
        quiz.option_texts = q.choices
        quiz.progress_text = f"{self.current_index + 1}/{len(self.active_questions)}"
        quiz.explanation_text = ""
        quiz.show_next = False

    def submit_answer(self, answer: str):
        if not self.active_questions:
            return
        quiz = self.root.get_screen("quiz")
        if quiz.show_next:
            return
        q = self.active_questions[self.current_index]
        if answer == q.answer:
            self.score += 1
        quiz.show_next = True
        quiz.explanation_text = "Loading explanation..."
        self.last_explanation = q.explanation

        def on_complete(text: str) -> None:
            quiz.explanation_text = text
            self.last_explanation = text

        def on_error(_message: str) -> None:
            quiz.explanation_text = q.explanation
            self.last_explanation = q.explanation

        if self.ai_engine.is_available():
            self.quiz_engine.get_explanation(q, answer, on_complete, on_error)
        else:
            on_error("")

    def next_question(self):
        self.current_index += 1
        self._load_question()

    def show_results(self):
        results = self.root.get_screen("results")
        total = len(self.active_questions)
        percent = int((self.score / total) * 100) if total else 0
        results.score_text = f"Score: {self.score}/{total} ({percent}%)"
        results.encouragement_text = ENCOURAGEMENTS[min(percent // 34, 2)]
        results.explanation_text = self.last_explanation
        self._store_results(percent)
        self.current_difficulty = self.quiz_engine.adapt_difficulty(percent)
        self.root.current = "results"

    def _store_results(self, percent: int) -> None:
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
    # AI TUTOR
    # -------------------------

    def send_tutor_question(self, question: str):
        question = question.strip()
        screen = self.root.get_screen("ai_tutor")
        if not question:
            screen.status_text = "Please enter a question."
            return
        screen.status_text = "Tutor is thinking..."
        screen.chat_history += f"\nYou: {question}\n"

        def on_complete(text: str) -> None:
            screen.chat_history += f"Tutor: {text}\n"
            screen.status_text = ""

        def on_error(message: str) -> None:
            screen.chat_history += f"Tutor: {message}\n"
            screen.status_text = ""

        if self.ai_engine.is_available():
            system_prompt = "You are a friendly AI tutor who answers in simple language."
            self.ai_engine.run_async(question, system_prompt, on_complete, on_error)
        else:
            on_error("AI features unavailable. Configure API key.")

    # -------------------------
    # PROGRESS
    # -------------------------

    def _refresh_progress(self):
        data = self.storage.load()
        scores = data.get("scores", [])
        average = int(sum(scores) / len(scores)) if scores else 0
        history = data.get("history", [])
        history_lines = [
            f"{item['date']} · {item['topic']} · {item['score']}%" for item in history
        ]
        screen = self.root.get_screen("progress")
        screen.average_score = average
        screen.streak_text = f"Streak: {data.get('streak', 0)} days"
        screen.history_text = "\n".join(history_lines) if history_lines else "No quizzes yet."

    # -------------------------
    # DAILY MOTIVATION
    # -------------------------

    def _refresh_daily_quote(self):
        home = self.root.get_screen("home")
        home.daily_quote = self.motivation_engine.get_daily_quote()

    def _refresh_motivation(self):
        home = self.root.get_screen("home")
        home.motivation_status = "Loading AI motivation..."

        def on_complete(text: str) -> None:
            home.motivation_status = text

        def on_error(message: str) -> None:
            home.motivation_status = message

        if self.ai_engine.is_available():
            self.motivation_engine.request_ai_motivation(on_complete, on_error)
        else:
            home.motivation_status = "AI features unavailable. Configure API key."

    # -------------------------
    # BACK BUTTON
    # -------------------------

    def _handle_back(self, _window, key, *_args):
        if key == 27:
            self.go_home()
            return True
        return False


if __name__ == "__main__":
    QuizAIApp().run()
