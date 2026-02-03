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

Window.clearcolor = (0.96, 0.97, 0.98, 1)


class QuizLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=15, **kwargs)

        self.add_widget(Label(text="S Quiz", font_size="26sp", bold=True))
        self.add_widget(Label(text="Smart Exam Preparation", font_size="14sp"))

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
            height="45dp"
        )
        self.add_widget(self.count_input)

        btn_box = BoxLayout(size_hint_y=None, height="45dp", spacing=10)

        file_btn = Button(text="Upload File")
        file_btn.bind(on_press=self.pick_file)
        btn_box.add_widget(file_btn)

        start_btn = Button(text="Start Exam")
        start_btn.bind(on_press=self.start_exam)
        btn_box.add_widget(start_btn)

        self.add_widget(btn_box)

        self.status = Label(text="")
        self.add_widget(self.status)

        self.question = Label(font_size="18sp")
        self.add_widget(self.question)

        self.options = BoxLayout(orientation="vertical", spacing=10)
        self.add_widget(self.options)

        self.text_data = ""
        self.quiz = []
        self.index = 0
        self.score = 0

    def pick_file(self, instance):
        chooser = FileChooserListView()
        popup = Popup(title="Select File", content=chooser, size_hint=(0.9, 0.9))

        def selected(_, files):
            if files:
                self.text_data = read_file(files[0])
                self.status.text = "File loaded"
                popup.dismiss()

        chooser.bind(selection=selected)
        popup.open()

    def start_exam(self, instance):
        count = int(self.count_input.text or 5)
        text = self.text_data or self.topic_input.text.strip()

        if not text or len(text) < 50:
            self.status.text = "Please enter valid content"
            return

        self.quiz = generate_quiz(text, count)
        if not self.quiz:
            self.status.text = "Failed to generate questions"
            return

        self.index = 0
        self.score = 0
        self.show_question()

    def show_question(self):
        self.options.clear_widgets()

        if self.index >= len(self.quiz):
            self.save_score()
            self.question.text = f"Exam Finished\nScore: {self.score}/{len(self.quiz)}"
            return

        q = self.quiz[self.index]
        self.question.text = q["question"]

        for opt in q["options"]:
            btn = Button(text=opt, size_hint_y=None, height="45dp")
            btn.bind(on_press=self.check_answer)
            self.options.add_widget(btn)

    def check_answer(self, instance):
        if instance.text == self.quiz[self.index]["answer"]:
            self.score += 1
        self.index += 1
        Clock.schedule_once(lambda dt: self.show_question(), 0.3)

    def save_score(self):
        app = App.get_running_app()
        path = os.path.join(app.user_data_dir, "scores.json")

        data = []
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)

        data.append({"score": self.score, "total": len(self.quiz)})

        with open(path, "w") as f:
            json.dump(data, f, indent=2)


class QuizApp(App):
    kv_file = None  # IMPORTANT

    def build(self):
        return QuizLayout()


QuizApp().run()
