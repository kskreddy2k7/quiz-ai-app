from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
import json, os

from file_reader import read_file
from quiz_generator import generate_quiz

Window.clearcolor = (0.95, 0.96, 0.98, 1)


class QuizLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=15)

        self.add_widget(Label(
            text="S Quiz",
            font_size="30sp",
            bold=True,
            color=(0.1, 0.2, 0.5, 1)
        ))

        self.add_widget(Label(
            text="Smart Exam Preparation",
            font_size="14sp",
            color=(0.4, 0.4, 0.4, 1)
        ))

        self.topic_input = TextInput(
            hint_text="Enter topic or upload study material",
            size_hint_y=None,
            height="45dp",
            multiline=False
        )
        self.add_widget(self.topic_input)

        self.count_input = TextInput(
            hint_text="Number of questions (default 5)",
            input_filter="int",
            size_hint_y=None,
            height="45dp"
        )
        self.add_widget(self.count_input)

        btns = BoxLayout(size_hint_y=None, height="50dp", spacing=10)

        upload = Button(text="📂 Upload File")
        upload.bind(on_press=self.pick_file)

        start = Button(text="▶ Start Exam", background_color=(0.1, 0.45, 0.85, 1))
        start.bind(on_press=self.start_exam)

        btns.add_widget(upload)
        btns.add_widget(start)
        self.add_widget(btns)

        self.question_label = Label(
            font_size="18sp",
            halign="left",
            valign="middle"
        )
        self.add_widget(self.question_label)

        self.options_box = BoxLayout(orientation="vertical", spacing=10)
        self.add_widget(self.options_box)

        self.explanation_label = Label(
            font_size="14sp",
            color=(0.2, 0.2, 0.2, 1)
        )
        self.add_widget(self.explanation_label)

        self.text_data = ""
        self.quiz = []
        self.index = 0
        self.score = 0

    def pick_file(self, _):
        chooser = FileChooserListView(
            path="/storage/emulated/0/Download",
            filters=["*.pdf", "*.docx", "*.pptx", "*.txt"]
        )
        popup = Popup(title="Select Study File", content=chooser, size_hint=(0.95, 0.95))

        def select(_, files):
            if files:
                self.text_data = read_file(files[0])
                popup.dismiss()

        chooser.bind(selection=select)
        popup.open()

    def start_exam(self, _):
        text = self.text_data or self.topic_input.text
        if not text:
            return

        count = int(self.count_input.text or 5)
        self.quiz = generate_quiz(text, count)
        self.index = 0
        self.score = 0
        self.show_question()

    def show_question(self):
        self.options_box.clear_widgets()
        self.explanation_label.text = ""

        if self.index >= len(self.quiz):
            self.question_label.text = f"Exam Completed\nScore: {self.score}/{len(self.quiz)}"
            return

        q = self.quiz[self.index]
        self.question_label.text = q["question"]

        for opt in q["options"]:
            btn = Button(text=opt, size_hint_y=None, height="45dp")
            btn.bind(on_press=self.check_answer)
            self.options_box.add_widget(btn)

    def check_answer(self, instance):
        q = self.quiz[self.index]

        if instance.text == q["answer"]:
            self.score += 1
            instance.background_color = (0.2, 0.8, 0.3, 1)
        else:
            instance.background_color = (0.9, 0.2, 0.2, 1)

        self.explanation_label.text = q["explanation"]
        self.index += 1
        Clock.schedule_once(lambda dt: self.show_question(), 2)


class QuizApp(App):
    def build(self):
        return QuizLayout()


QuizApp().run()
