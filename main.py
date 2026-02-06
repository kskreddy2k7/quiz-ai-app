from __future__ import annotations

import datetime
import os
from pathlib import Path
from typing import List

try:
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.lang import Builder
    from kivy.metrics import dp
    from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, StringProperty
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.popup import Popup
    from kivy.uix.screenmanager import ScreenManager
except ImportError:
    import sys
    print("\n" + "="*60)
    print("CRITICAL ERROR: Kivy framework not found.")
    print("="*60)
    if sys.version_info >= (3, 13):
        print(f"You are running Python {sys.version_info.major}.{sys.version_info.minor}, which is too new for Kivy.")
        print("Please install Python 3.10, 3.11, or 3.12 to run this app.")
    else:
        print("Please install dependencies using: pip install -r requirements.txt")
    print("="*60 + "\n")
    sys.exit(1)

import os
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
except ImportError:
    pass

# --- Service Imports ---
from app.services.ai_service import AIService
from app.services.quiz_service import QuizService, QuizQuestion
from app.services.tutor_service import TutorService
from app.services.storage_service import StorageService

# --- Utils Imports ---
from app.utils.permissions import PermissionManager
from app.utils.helpers import build_daily_quote

# --- UI Imports ---
# Guard these as well if they import kivy at top level (they do)
try:
    from app.screens.ai_chat import AIChatScreen
    from app.screens.explanation import ExplanationScreen
    from app.screens.home import HomeScreen
    from app.screens.progress import ProgressScreen
    from app.screens.quiz_play import QuizPlayScreen
    from app.screens.quiz_setup import QuizSetupScreen
    from app.screens.results import ResultsScreen
    from app.screens.settings import SettingsScreen
    from app.screens.splash import SplashScreen
except ImportError:
    pass # Already caught above, app won't run anyway


ENCOURAGEMENTS = [
    "🌟 Great effort! Keep going!",
    "🔥 Well done! You're improving!",
    "🚀 Fantastic work! Stay consistent!",
]


class QuizAIApp(App):
    title = "S Quiz by Sai"
    has_gradient = BooleanProperty(False)

    current_index = NumericProperty(0)
    score = NumericProperty(0)

    active_questions: List[QuizQuestion]
    last_topic: str = "General"
    current_difficulty: str = "easy"
    last_explanation: str = ""
    last_selected_answer: str = ""
    user_answers: dict = {}  # Map index -> selected_answer
    language = StringProperty("English") # Added Language Property
    
    # -------------------------
    # CONFIG
    # -------------------------
    # TODO: Replace with your actual Render/Railway URL after deployment
    # Example: "https://quiz-ai-backend.onrender.com"
    BACKEND_URL = "https://s-quiz-lo7f.onrender.com"

    # -------------------------
    # APP STARTUP
    # -------------------------

    def build(self):
        # Mobile app window setup
        from kivy.core.window import Window
        Window.clearcolor = (0.06, 0.09, 0.16, 1)  # Dark background
        
        self.active_questions = []
        self.user_answers = {}

        # INSTANTIATE SERVICES (minimal for build, full init in on_start)
        self.storage_service = StorageService("quiz_data.json")
        self.ai_service = AIService() # Placeholder, will be re-initialized in on_start
        
        # Determine local questions path safely
        try:
            if self.user_data_dir:
                local_q_path = Path(self.user_data_dir) / "local_questions.json"
            else:
                local_q_path = Path(__file__).resolve().parent / "local_questions.json"
        except Exception:
            local_q_path = Path("local_questions.json")
        
        self.quiz_service = QuizService(self.ai_service, local_q_path)
        self.tutor_service = TutorService(self.ai_service)
        self.permission_manager = PermissionManager()

        self._load_kv_files()

        manager = ScreenManager()
        manager.add_widget(SplashScreen(name="splash"))
        manager.add_widget(HomeScreen(name="home"))
        manager.add_widget(AIChatScreen(name="ai_chat"))
        manager.add_widget(QuizSetupScreen(name="quiz_setup"))
        manager.add_widget(QuizPlayScreen(name="quiz_play"))
        manager.add_widget(ExplanationScreen(name="explanation"))
        manager.add_widget(ResultsScreen(name="results"))
        manager.add_widget(SettingsScreen(name="settings"))
        manager.add_widget(ProgressScreen(name="progress"))

        return manager

    def _data_path(self, filename: str) -> Path:
        return Path(__file__).resolve().parent / "app" / "data" / filename

    def _load_kv_files(self) -> None:
        try:
            # Use a more robust path discovery
            base_dir = Path(__file__).resolve().parent
            ui_dir = base_dir / "app" / "ui"
            
            # Fallback if app structure is different on device
            if not ui_dir.exists():
                ui_dir = base_dir / "ui"
            
            kv_files = [
                "splash.kv", "home.kv", "ai_chat.kv", 
                "quiz_setup.kv", "quiz_play.kv", "explanation.kv", 
                "results.kv", "settings.kv", "progress.kv"
            ]
            for file in kv_files:
                path = ui_dir / file
                if path.exists():
                    print(f"DEBUG: Loading {file}...")
                    Builder.load_file(str(path))
                else:
                    print(f"WARNING: Could not find {file} at {path}")
        except Exception as e:
            print(f"CRITICAL: Failed to load KV files: {e}")

    def on_start(self):
        # Startup checks & Service Initialization
        self.ai_service = AIService(backend_url=self.BACKEND_URL)
        self.quiz_service.ai_service = self.ai_service
        self.tutor_service.ai_service = self.ai_service
        
        print(f"DEBUG Mobile AI Status: {self.ai_service.availability_message()}")
        
        # Start initial data loading
        Clock.schedule_once(lambda dt: self._load_initial_data(), 1)

    def _load_initial_data(self):
        """Loads quotes and status after app has drawn."""
        self._refresh_daily_quote()
        self._refresh_ai_status()

    # ... (other methods unchanged) ...

    def request_daily_motivation(self):
        home = self.root.get_screen("home")
        if not self.ai_service.is_available():
            try:
                home.motivation_status = "📴 Offline: Keep learning!"
            except AttributeError:
                pass
            return

        try:
            home.motivation_status = "✨ Loading motivation..."
        except AttributeError:
            pass

        def on_complete(text: str):
            try:
                home.motivation_status = text
            except AttributeError:
                pass

        def on_error(_msg: str):
            try:
                home.motivation_status = "Keep pushing forward! 🚀"
            except AttributeError:
                pass

        self.ai_service.solve_doubt(
            "Give a short study motivation with emojis. Max 10 words.",
            on_complete,
            on_error,
        )
        Clock.schedule_once(self._go_home_from_splash, 1.5)

    # -------------------------
    # NAVIGATION
    # -------------------------

    def _go_home_from_splash(self, _dt):
        self.root.current = "home"
        Clock.schedule_once(self._request_permissions, 0.5)
        Clock.schedule_once(self._maybe_show_first_launch_dialog, 0.8)

    def go_home(self):
        self._refresh_daily_quote()
        self._refresh_ai_status()
        self.root.current = "home"

    def go_ai_chat(self):
        screen = self.root.get_screen("ai_chat")
        if self.ai_service.is_available():
            screen.status_text = ""
        else:
            screen.status_text = "📴 AI tutor is offline. Try a quiz instead."
        self.root.current = "ai_chat"

    def go_quiz_setup(self, mode: str = "file"):
        screen = self.root.get_screen("quiz_setup")
        screen.mode = mode
        # Ensure subjects.json exists or handle it
        subjects_path = self._data_path("subjects.json")
        if subjects_path.exists():
            screen.load_subjects(subjects_path)
        self.root.current = "quiz_setup"

    def go_progress(self):
        self._refresh_progress()
        self.root.current = "progress"

    def open_settings(self):
        self.root.current = "settings"

    def go_results_overview(self):
        # Navigation to results or a new analytics screen
        # For now, we reuse the results logic or redirect to progress
        self.root.current = "progress"

    # -------------------------
    # PERMISSIONS
    # -------------------------

    def _request_permissions(self, _dt):
        home = self.root.get_screen("home")
        try:
            home.permission_status = "Requesting permissions…"
        except AttributeError:
             pass # UI might not have this property yet

        def update(msg: str):
            try:
                home.permission_status = msg
            except AttributeError:
                pass

        self.permission_manager.request_permissions(update)

    # -------------------------
    # QUIZ FLOW
    # -------------------------

    def start_quiz(
        self, 
        subject: str, 
        topic: str, 
        difficulty: str, 
        content_context: str = "",
        file_path: str = "",
        num_questions: int = 5,
        q_type: str = "mixed"
    ):
        self.last_topic = f"{subject} · {topic}" if topic else subject
        self.current_difficulty = difficulty or "easy"
        self.root.current = "quiz_play"

        quiz = self.root.get_screen("quiz_play")
        quiz.question_text = f"🧠 Analyzing in {self.language}..." if file_path or content_context else f"🧠 Preparing {self.language} quiz..."
        quiz.option_texts = []
        quiz.progress_text = ""

        def on_complete(questions: List[QuizQuestion]):
            self._start_questions(questions)

        def on_error(_msg: str):
            # Fallback to local database if everything else fails
            quiz.progress_text = f"⚠️ Generation error: {_msg}. Reverting to local library..."
            questions = self.quiz_service.get_local_quiz(
                subject, topic, self.current_difficulty
            )
            self._start_questions(questions)

        # Logic:
        # 1. If we have custom context (File/Text), ALWAYS try generation (AI or Mock)
        # 2. If no context, check AI availability.
        #    - If Available: AI Gen
        #    - If Offline: Local DB (Mock gen is bad without source text)
        
        has_context = bool(content_context or file_path)
        
        if has_context or self.ai_service.is_available():
            quiz.progress_text = "✨ generating quiz..."
            self.quiz_service.request_ai_quiz(
                subject=subject, 
                topic=topic, 
                difficulty=self.current_difficulty,
                content_context=content_context, 
                file_path=file_path,
                num_questions=num_questions,
                q_type=q_type,
                language=self.language,
                on_complete=on_complete, 
                on_error=on_error
            )
        else:
            on_error("offline_no_context")

    def cycle_language(self):
        langs = ["English", "Hindi", "Telugu"]
        try:
            current_idx = langs.index(self.language)
            next_idx = (current_idx + 1) % len(langs)
            self.language = langs[next_idx]
        except ValueError:
            self.language = "English"

    def _start_questions(self, questions: List[QuizQuestion]):
        if not questions:
            quiz = self.root.get_screen("quiz_play")
            quiz.question_text = "No questions available offline."
            quiz.option_texts = []
            return

        self.active_questions = questions
        self.current_index = 0
        self.score = 0
        self.user_answers = {}
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
        self.user_answers[self.current_index] = answer

        if answer == q.answer:
            self.score += 1
            
        # Move to next question immediately (Test first, review later)
        self.next_question()

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
        self.root.current = "results"

    def _store_results(self, percent: int):
        today = datetime.date.today().isoformat()
        streak = self.storage_service.update_streak(today)

        self.storage_service.add_history(
            {
                "date": today,
                "topic": self.last_topic,
                "difficulty": self.current_difficulty,
                "score": percent,
            }
        )

        self.storage_service.update_score(percent)
        home = self.root.get_screen("home")
        try:
            home.streak_text = f"Streak: {streak} days"
        except AttributeError:
             pass

    # -------------------------
    # AI CHAT
    # -------------------------

    def send_ai_question(self, question: str):
        screen = self.root.get_screen("ai_chat")
        # Delegate to the screen which handles the UI logic
        screen.send_message(question)



    def ask_about_review_item(self, question: str, answer_info: str):
        # Strip markup and formatting
        import re
        clean_ans = re.sub(r'\[.*?\]', '', answer_info)
        context_q = f"In a quiz, I had this question: \"{question}\". {clean_ans}. Can you explain the concepts involved in more detail?"
        
        # Navigate and send
        self.go_ai_chat()
        screen = self.root.get_screen("ai_chat")
        screen.send_message(context_q)

    # -------------------------
    # PROGRESS
    # -------------------------

    def _refresh_progress(self):
        data = self.storage_service.load()
        scores = data.get("scores", [])
        avg = int(sum(scores) / len(scores)) if scores else 0

        history = data.get("history", [])
        lines = [f"{i['date']} · {i['topic']} · {i['score']}%" for i in history]

        screen = self.root.get_screen("progress")
        try:
            screen.average_score = avg
            screen.streak_text = f"Streak: {data.get('streak', 0)} days"
            screen.history_text = "\n".join(lines) if lines else "No quizzes yet."
        except AttributeError:
             pass

    # -------------------------
    # DAILY MOTIVATION
    # -------------------------

    def _refresh_daily_quote(self):
        home = self.root.get_screen("home")
        try:
            home.daily_quote = build_daily_quote()
        except AttributeError:
            pass
        self._refresh_ai_status()

    def _refresh_ai_status(self):
        home = self.root.get_screen("home")
        available = self.ai_service.is_available()
        try:
            home.ai_available = available
            home.ai_status = self.ai_service.availability_message()
            home.ai_status_color = (
                [0.6, 1, 0.7, 1] if available else [0.8, 0.85, 0.95, 0.9]
            )
        except AttributeError:
            pass

    def _maybe_show_first_launch_dialog(self, _dt):
        data = self.storage_service.load()
        if data.get("first_launch_shown"):
            return
        message = (
            "Welcome to Quiz AI! 📘\n\n"
            "• Works offline with demo quizzes\n"
            "• AI features need internet + API key\n"
            "• We do not collect personal data"
        )
        from app.ui.theme import Theme
        content = BoxLayout(orientation="vertical", spacing="12dp", padding="12dp")
        content.add_widget(
            Label(
                text=message,
                halign="left",
                valign="middle",
                color=Theme.get_color(Theme.TEXT_PRIMARY),
                text_size=(dp(300), None),
                font_name=Theme.FONT_BODY,
            )
        )
        
        # Styled Button equivalent
        btn = Button(
            text="Got it", 
            size_hint_y=None, 
            height=dp(44),
            background_normal="",
            background_color=Theme.get_color(Theme.PRIMARY_START),
            color=Theme.get_color(Theme.TEXT_PRIMARY),
            font_name=Theme.FONT_BUTTON,
            bold=True
        )
        content.add_widget(btn)
        
        popup = Popup(
            title="First-time Info",
            title_font=Theme.FONT_HEADINGS,
            content=content,
            size_hint=(0.85, None),
            height=dp(320),
            auto_dismiss=False,
            separator_color=Theme.get_color(Theme.PRIMARY_START)
        )
        btn.bind(on_release=popup.dismiss)
        popup.open()
        self.storage_service.mark_first_launch_shown()

    def _format_wrong_explanations(self, question: QuizQuestion) -> str:
        if not question.wrong_explanations:
            return "No additional details available."
        lines = []
        for choice in question.choices:
            if choice == question.answer:
                continue
            explanation = question.wrong_explanations.get(
                choice, "This option is incorrect."
            )
            lines.append(f"• {choice}: {explanation}")
        return "\n".join(lines)

    def request_daily_motivation(self):
        home = self.root.get_screen("home")
        if not self.ai_service.is_available():
            try:
                home.motivation_status = "📴 Offline: Keep learning!"
            except AttributeError:
                pass
            return

        try:
            home.motivation_status = "✨ Loading motivation..."
        except AttributeError:
            pass

        def on_complete(text: str):
            try:
                home.motivation_status = text
            except AttributeError:
                pass

        def on_error(_msg: str):
            try:
                home.motivation_status = "📴 Offline: Keep learning!"
            except AttributeError:
                pass

        self.ai_service.run_async(
            "Give a short study motivation with emojis.",
            "You are a motivating tutor.",
            on_complete,
            on_error,
        )


if __name__ == "__main__":
    QuizAIApp().run()
