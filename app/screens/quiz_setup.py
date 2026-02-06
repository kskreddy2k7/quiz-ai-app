from __future__ import annotations

import json
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ListProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.spinner import Spinner

from app.ui.theme import Theme


class QuizSetupScreen(Screen):
    subjects = ListProperty([])
    selected_subject = StringProperty("")
    
    topics = ListProperty([])
    selected_topic = StringProperty("")

    difficulties = ListProperty(["Easy", "Medium", "Hard"])
    selected_difficulty = StringProperty("Easy")

    # New: Custom Context & Config
    custom_text = StringProperty("")
    file_path = StringProperty("")
    file_text_cache = StringProperty("") # Store extracted text here for preview/validation
    
    num_questions = NumericProperty(5)
    question_type = StringProperty("Mixed")
    mode = StringProperty("file")
    
    is_loading = BooleanProperty(False)
    status_text = StringProperty("")
    upload_status = StringProperty("No file uploaded")
    can_generate = BooleanProperty(False)
    
    # UI State Properties
    topic_height = NumericProperty(0)
    topic_opacity = NumericProperty(0)
    topic_disabled = BooleanProperty(True)
    topic_padding = ListProperty([0, 0, 0, 0])
    
    file_height = NumericProperty(0)
    file_opacity = NumericProperty(0)
    file_disabled = BooleanProperty(True)
    file_padding = ListProperty([0, 0, 0, 0])

    _popup = None
    
    def on_mode(self, instance, value):
        self._update_visibility()

    def _update_visibility(self):
        from kivy.metrics import dp
        if self.mode == "topic":
             self.topic_height = self.ids.topic_card.minimum_height if self.ids.topic_card else dp(400)
             self.topic_opacity = 1
             self.topic_disabled = False
             self.topic_padding = [dp(20), dp(20), dp(20), dp(20)]
             
             self.file_height = 0
             self.file_opacity = 0
             self.file_disabled = True
             self.file_padding = [0, 0, 0, 0]
        else:
             self.topic_height = 0
             self.topic_opacity = 0
             self.topic_disabled = True
             self.topic_padding = [0, 0, 0, 0]
             
             self.file_height = dp(300)
             self.file_opacity = 1
             self.file_disabled = False
             self.file_padding = [dp(20), dp(20), dp(20), dp(20)]

    def open_file_chooser(self):
        # Create a visually improved file chooser popup
        from kivy.uix.popup import Popup
        from kivy.uix.filechooser import FileChooserIconView
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        
        main_layout = BoxLayout(orientation="vertical", spacing="12dp", padding="12dp")
        
        # --- Shortcuts Bar ---
        shortcuts_layout = BoxLayout(size_hint_y=None, height="44dp", spacing="8dp")
        
        def set_path(path_str):
            chooser.path = str(path_str)

        home = Path.home()
        shortcuts = {
            "🏠 Home": home,
            "📥 Downloads": home / "Downloads",
            "📄 Docs": home / "Documents",
            "🖥️ Desktop": home / "Desktop"
        }
        
        for name, p in shortcuts.items():
            if p.exists():
                btn = Button(text=name, size_hint_x=None, width="100dp", font_size="12sp")
                btn.bind(on_release=lambda instance, p=p: set_path(p))
                shortcuts_layout.add_widget(btn)

        main_layout.add_widget(shortcuts_layout)
        
        # --- File Chooser ---
        chooser = FileChooserIconView(
            path=str(home / "Downloads") if (home / "Downloads").exists() else str(home),
            filters=["*.pdf", "*.docx", "*.txt", "*.PDF", "*.DOCX", "*.TXT"],
            size_hint_y=1,
            multiselect=False
        )
        main_layout.add_widget(chooser)
        
        # --- Action Buttons ---
        btn_layout = BoxLayout(size_hint_y=None, height="48dp", spacing="10dp")
        btn_cancel = Button(text="Cancel", background_color=[0.8, 0.3, 0.3, 1])
        btn_select = Button(text="Open Selected ✅", background_color=[0.3, 0.8, 0.5, 1])
        
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_select)
        main_layout.add_widget(btn_layout)
        
        self._popup = Popup(
            title="Choose Source Material (PDF/DOCX/TXT)", 
            content=main_layout, 
            size_hint=(0.95, 0.95)
        )
        
        def handle_file(selection):
            print(f"DEBUG: File Selection Triggered: {selection}")
            if selection:
                path = selection[0]
                # Normalize path for Windows
                import os
                norm_path = os.path.normpath(path)
                print(f"DEBUG: Normalized Path: {norm_path}")
                self.file_path = norm_path
                self._extract_text_preview(norm_path)
                self._popup.dismiss()
            else:
                self.status_text = "⚠️ No file selected. Please click on a file first."

        def on_select(instance):
            handle_file(chooser.selection)
            
        btn_cancel.bind(on_release=self._popup.dismiss)
        btn_select.bind(on_release=on_select)
        # Support double-click
        chooser.bind(on_submit=lambda instance, selection, touch: handle_file(selection))
        
        self._popup.open()

    def _extract_text_preview(self, path):
        # Extract immediately to validate
        app = App.get_running_app()
        self.upload_status = "⌛ Extracting text..."
        self.can_generate = False
        
        try:
            text = app.quiz_service.file_service.extract_text(path)
            if not text or len(text.strip()) < 50:
                self.file_text_cache = ""
                self.upload_status = "❌ Error: File is empty or too short."
                self.can_generate = False
            else:
                self.file_text_cache = text
                self.upload_status = "✅ Upload Success! Text extracted."
                self.can_generate = True
                
        except Exception as e:
            self.file_text_cache = ""
            self.upload_status = f"❌ Error: {str(e)}"
            self.can_generate = False
            self.status_text = f"Extraction failed: {str(e)}"
            print(f"Extraction Error: {e}")

    def on_enter(self):
        # Ensure UI is correctly updated based on mode
        self._update_visibility()
        
        # Load subjects
        app = App.get_running_app()
        subjects_path = app._data_path("subjects.json")
        self.load_subjects(subjects_path)

    def load_subjects(self, path: Path):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self.subjects = list(data.keys())
        except (OSError, json.JSONDecodeError):
            self.subjects = ["General", "Science", "Math", "History"]

    def set_subject(self, subject: str, path: Path = None):
        self.selected_subject = subject
        self.selected_topic = ""
        
        # Load topics if file provided
        if path and path.exists():
             try:
                data = json.loads(path.read_text(encoding="utf-8"))
                self.topics = data.get(subject, [])
             except:
                 self.topics = []
        else:
            self.topics = []

    def set_topic(self, topic: str):
        self.selected_topic = topic

    def set_difficulty(self, diff: str):
        self.selected_difficulty = diff

    def create_quiz(self):
        print(f"DEBUG: Create Quiz Triggered. Mode: {self.mode}")
        app = App.get_running_app()
        subject = self.selected_subject or "General"
        topic = self.selected_topic
        difficulty = self.selected_difficulty.lower()
        
        # Combine cache and manual paste (Strict Content Lock)
        final_context = (self.file_text_cache + "\n" + self.custom_text).strip()
        print(f"DEBUG: Final Context Length: {len(final_context)}")
        
        # Validation for FILE mode
        if self.mode == "file":
            if len(final_context) < 50:
                 self.status_text = "⚠️ Please upload a valid file or paste more text (min 50 chars)."
                 return
        else:
            # Topic mode: context is optional but we can send custom text if user pasted something
            pass

        # Pass context to main app handler
        app.start_quiz(
            subject=subject, 
            topic=topic, 
            difficulty=difficulty, 
            content_context=final_context, # Use strictly validated text
            file_path="",  # We already extracted it, so no need to re-extract in service
            num_questions=self.num_questions,
            q_type=self.question_type
        )
