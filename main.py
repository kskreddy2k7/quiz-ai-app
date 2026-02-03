from kivy.core.window import Window
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.clock import Clock
import json
import os

from file_reader import read_file
from quiz_generator import generate_quiz

# ---------- THEME ----------
Window.clearcolor = (0.96, 0.97, 0.98, 1)


class QuizLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=15, **kwargs)

        # ---------- HEADER ----------
        self.add_widget(Label(
            text="S Quiz",
            font_size="26sp",
            bold=True,
            color=(0.1, 0.2, 0.4, 1),
            size_hint_y=None,
            height="45dp"
        ))

        self.add_widget(Label(
            text="Smart Exam Preparation",
            font_size="14sp",
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height="30dp"
        ))

        # ---------- INPUTS ----------
        self.topic_input = TextInput(
            hint_text="Enter topic OR upload study file",
            size_hint_y=None,
            height="45dp",
            multiline=False
        )
        self.add_widget(self.topic_input)

        self.count_input = TextInput(
            hint_text="Number of questions",
            input_filter="int",
            size_hint_y=None,
            height="45dp",
            multiline=False
        )
        self.add_widget(self.count_input)

        # ---------- BUTTONS ----------
        btn_box = BoxLayout(size_hint_y=None, height="45dp", spacing=10)

        file_btn = Button(
            text="Upload File",
            background_normal="",
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1)
        )
        file_btn.bind(on_press=self.pick_file)
        btn_box.add_widget(file_btn)

        start_btn = Button(
            text="Start Exam",
            background_normal="",
            background_color=(0.12, 0.45, 0.85, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        start_btn.bind(on_press=self.start_exam)
        btn_box.add_widget(start_btn)

        self.add_widget(btn_box)

        # ---------- STATUS ----------
        self.status = Label(text="", font_size="14sp")
        self.add_widget(self.status)

        # ---------- QUESTION ----------
        self.question_label = Label(
            text="",
            font_size="18sp",
            bold=True,
            size_hint_y=None,
            height="100dp"
        )
        self.add_widget(self.question_label)

        # ---------- OPTIONS ----------
        self.options_box = BoxLayout(orientation="vertical", spacing=10)
        self.add_widget(self.options_box)

        # ---------- STATE ----------
        self.text_data = ""
        self.quiz = []
        self.index = 0
        self.score = 0

    # ---------- FILE PICKER ----------
    def pick_file(self, instance):
        chooser = FileChooserListView(path="/sdcard/Download")
        popup = Popup(
            title="Select Study File",
            content=chooser,
            size_hint=(0.9, 0.9)
        )

        def selected(_, files):
            if files:
                self.text_data = read_file(files[0])
                self.status.text = "File loaded successfully"
                popup.dismiss()

        chooser.bind(selection=selected)
        popup.open()

    # ---------- START EXAM ----------
    def start_exam(self, instance):
        count = int(self.count_input.text or 5)

        text = self.text_data if self.text_data else self.topic_input.text.strip()
        if not text:
            self.status.text = "Enter a topic or upload a file"
            return

        self.quiz = generate_quiz(text, count)
        self.index = 0
        self.score = 0
        self.status.text = ""

        if not self.quiz:
            self.status.text = "Could not generate questions"
            return

        self.show_question()

    # ---------- SHOW QUESTION ----------
    def show_question(self):
        self.options_box.clear_widgets()

        if self.index >= len(self.quiz):
            self.save_score()
            self.question_label.text = f"Exam Finished\nScore: {self.score}/{len(self.quiz)}"
            return

        q = self.quiz[self.index]
        self.question_label.text = q["question"]

        for option in q["options"]:
            btn = Button(
                text=option,
                size_hint_y=None,
                height="48dp",
                background_normal="",
                background_color=(0.15, 0.55, 0.95, 1),
                color=(1, 1, 1, 1),
                bold=True
            )
            btn.bind(on_press=self.check_answer)
            self.options_box.add_widget(btn)

    # ---------- CHECK ANSWER ----------
    def check_answer(self, instance):
        correct = self.quiz[self.index]["answer"]

        if instance.text == correct:
            self.score += 1
            instance.background_color = (0.2, 0.8, 0.2, 1)
        else:
            instance.background_color = (0.9, 0.2, 0.2, 1)

        self.index += 1
        Clock.schedule_once(lambda dt: self.show_question(), 0.5)

    # ---------- SAVE SCORE (ANDROID SAFE) ----------
    def save_score(self):
        app = App.get_running_app()
        path = os.path.join(app.user_data_dir, "scores.json")

        data = []
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)

        data.append({"score": self.score, "total": len(self.quiz)})

        with open(path, "w") as f:
            json.dump(data, f, indent=2)


class QuizApp(App):
    kv_file = None  # IMPORTANT: disable auto .kv loading

    def build(self):
        return QuizLayout()


QuizApp().run()
