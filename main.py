from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.core.window import Window
from android.permissions import request_permissions, Permission
import json, os

from file_reader import read_file
from quiz_generator import generate_quiz

Window.clearcolor = (0.96, 0.97, 0.99, 1)


class QuizLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=15, **kwargs)

        # 🔐 Runtime permission (VERY IMPORTANT)
        if os.name == "posix":
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

        # 🌱 APP INTRO
        self.add_widget(Label(
            text="🌱 Welcome to S Quiz",
            font_size="26sp",
            bold=True,
            color=(0.1, 0.3, 0.6, 1)
        ))

        self.add_widget(Label(
            text=(
                "Learning is a journey, not a race.\n\n"
                "This app is built to help students improve step by step.\n\n"
                "— Kata Sai Kranthu Reddy"
            ),
            font_size="14sp",
            halign="center",
            color=(0.3, 0.3, 0.3, 1)
        ))

        # 📘 INPUTS
        self.topic_input = TextInput(
            hint_text="Enter topic OR upload study material",
            size_hint_y=None, height="45dp", multiline=False
        )
        self.add_widget(self.topic_input)

        self.count_input = TextInput(
            hint_text="Number of questions (default 5)",
            input_filter="int",
            size_hint_y=None, height="45dp"
        )
        self.add_widget(self.count_input)

        self.level_spinner = Spinner(
            text="Easy",
            values=("Easy", "Medium", "Hard"),
            size_hint_y=None, height="45dp"
        )
        self.add_widget(self.level_spinner)

        self.mode_spinner = Spinner(
            text="Practice",
            values=("Practice", "Exam"),
            size_hint_y=None, height="45dp"
        )
        self.add_widget(self.mode_spinner)

        # 🎯 BUTTONS
        btns = BoxLayout(size_hint_y=None, height="50dp", spacing=10)

        upload_btn = Button(text="📂 Upload File")
        upload_btn.bind(on_press=self.pick_file)

        start_btn = Button(
            text="▶ Start Learning",
            background_color=(0.1, 0.5, 0.9, 1)
        )
        start_btn.bind(on_press=self.start_exam)

        btns.add_widget(upload_btn)
        btns.add_widget(start_btn)
        self.add_widget(btns)

        # 📊 STATUS
        self.status = Label(text="", color=(0.2, 0.2, 0.2, 1))
        self.add_widget(self.status)

        self.timer_label = Label(text="")
        self.add_widget(self.timer_label)

        self.question_label = Label(
            text="", font_size="18sp", bold=True, halign="left", valign="middle"
        )
        self.add_widget(self.question_label)

        self.options_box = BoxLayout(orientation="vertical", spacing=10)
        self.add_widget(self.options_box)

        # 📦 STATE
        self.text_data = ""
        self.quiz = []
        self.index = 0
        self.score = 0
        self.exam_mode = False

        self.load_analytics()

    # 📂 FILE PICKER
    def pick_file(self, _):
        chooser = FileChooserListView(
            path="/storage/emulated/0",
            filters=["*.pdf", "*.docx", "*.pptx", "*.txt"]
        )
        popup = Popup(title="Select Study File", content=chooser, size_hint=(0.9, 0.9))

        def selected(_, files):
            if files:
                self.text_data = read_file(files[0])
                self.status.text = "✅ Study material loaded"
                popup.dismiss()

        chooser.bind(selection=selected)
        popup.open()

    # ▶ START
    def start_exam(self, _):
        count = int(self.count_input.text or 5)
        level = self.level_spinner.text.lower()
        self.exam_mode = self.mode_spinner.text == "Exam"

        text = self.text_data or self.topic_input.text.strip()
        if not text:
            self.status.text = "⚠ Please enter a topic or upload a file"
            return

        self.quiz = generate_quiz(text, count, level)
        self.index = 0
        self.score = 0

        if self.exam_mode:
            self.time_left = count * 20
            self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        else:
            self.timer_label.text = "🧪 Practice Mode (No timer)"

        self.show_question()

    # ⏱ TIMER
    def update_timer(self, dt):
        self.time_left -= 1
        self.timer_label.text = f"⏳ Time Left: {self.time_left}s"
        if self.time_left <= 0:
            Clock.unschedule(self.timer_event)
            self.finish_exam()

    # ❓ QUESTIONS
    def show_question(self):
        self.options_box.clear_widgets()

        if self.index >= len(self.quiz):
            self.finish_exam()
            return

        q = self.quiz[self.index]
        self.question_label.text = f"Q{self.index+1}. {q['question']}"

        for opt in q["options"]:
            btn = Button(text=opt, size_hint_y=None, height="48dp")
            btn.bind(on_press=self.check_answer)
            self.options_box.add_widget(btn)

    def check_answer(self, btn):
        q = self.quiz[self.index]

        if btn.text == q["answer"]:
            self.score += 1
            btn.background_color = (0.2, 0.8, 0.4, 1)
        else:
            btn.background_color = (0.9, 0.3, 0.3, 1)

        if not self.exam_mode:
            self.question_label.text += "\n\n💡 Explanation:\n" + q["explanation"]

        self.index += 1
        Clock.schedule_once(lambda dt: self.show_question(), 1)

    # 🏁 FINISH
    def finish_exam(self):
        self.question_label.text = (
            f"🎉 Well done!\n\nScore: {self.score}/{len(self.quiz)}\n\n"
            "Keep practicing. Improvement comes with consistency."
        )
        self.options_box.clear_widgets()
        self.save_analytics()

    # 📊 ANALYTICS
    def load_analytics(self):
        self.analytics = {"attempts": 0, "questions": 0, "correct": 0}
        if os.path.exists("analytics.json"):
            with open("analytics.json") as f:
                self.analytics = json.load(f)

    def save_analytics(self):
        self.analytics["attempts"] += 1
        self.analytics["questions"] += len(self.quiz)
        self.analytics["correct"] += self.score
        with open("analytics.json", "w") as f:
            json.dump(self.analytics, f, indent=2)


class QuizApp(App):
    def build(self):
        return QuizLayout()


if __name__ == "__main__":
    QuizApp().run()from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.core.window import Window
from android.permissions import request_permissions, Permission
import json, os

from file_reader import read_file
from quiz_generator import generate_quiz

Window.clearcolor = (0.96, 0.97, 0.99, 1)


class QuizLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=15, **kwargs)

        # 🔐 Runtime permission (VERY IMPORTANT)
        if os.name == "posix":
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

        # 🌱 APP INTRO
        self.add_widget(Label(
            text="🌱 Welcome to S Quiz",
            font_size="26sp",
            bold=True,
            color=(0.1, 0.3, 0.6, 1)
        ))

        self.add_widget(Label(
            text=(
                "Learning is a journey, not a race.\n\n"
                "This app is built to help students improve step by step.\n\n"
                "— Kata Sai Kranthu Reddy"
            ),
            font_size="14sp",
            halign="center",
            color=(0.3, 0.3, 0.3, 1)
        ))

        # 📘 INPUTS
        self.topic_input = TextInput(
            hint_text="Enter topic OR upload study material",
            size_hint_y=None, height="45dp", multiline=False
        )
        self.add_widget(self.topic_input)

        self.count_input = TextInput(
            hint_text="Number of questions (default 5)",
            input_filter="int",
            size_hint_y=None, height="45dp"
        )
        self.add_widget(self.count_input)

        self.level_spinner = Spinner(
            text="Easy",
            values=("Easy", "Medium", "Hard"),
            size_hint_y=None, height="45dp"
        )
        self.add_widget(self.level_spinner)

        self.mode_spinner = Spinner(
            text="Practice",
            values=("Practice", "Exam"),
            size_hint_y=None, height="45dp"
        )
        self.add_widget(self.mode_spinner)

        # 🎯 BUTTONS
        btns = BoxLayout(size_hint_y=None, height="50dp", spacing=10)

        upload_btn = Button(text="📂 Upload File")
        upload_btn.bind(on_press=self.pick_file)

        start_btn = Button(
            text="▶ Start Learning",
            background_color=(0.1, 0.5, 0.9, 1)
        )
        start_btn.bind(on_press=self.start_exam)

        btns.add_widget(upload_btn)
        btns.add_widget(start_btn)
        self.add_widget(btns)

        # 📊 STATUS
        self.status = Label(text="", color=(0.2, 0.2, 0.2, 1))
        self.add_widget(self.status)

        self.timer_label = Label(text="")
        self.add_widget(self.timer_label)

        self.question_label = Label(
            text="", font_size="18sp", bold=True, halign="left", valign="middle"
        )
        self.add_widget(self.question_label)

        self.options_box = BoxLayout(orientation="vertical", spacing=10)
        self.add_widget(self.options_box)

        # 📦 STATE
        self.text_data = ""
        self.quiz = []
        self.index = 0
        self.score = 0
        self.exam_mode = False

        self.load_analytics()

    # 📂 FILE PICKER
    def pick_file(self, _):
        chooser = FileChooserListView(
            path="/storage/emulated/0",
            filters=["*.pdf", "*.docx", "*.pptx", "*.txt"]
        )
        popup = Popup(title="Select Study File", content=chooser, size_hint=(0.9, 0.9))

        def selected(_, files):
            if files:
                self.text_data = read_file(files[0])
                self.status.text = "✅ Study material loaded"
                popup.dismiss()

        chooser.bind(selection=selected)
        popup.open()

    # ▶ START
    def start_exam(self, _):
        count = int(self.count_input.text or 5)
        level = self.level_spinner.text.lower()
        self.exam_mode = self.mode_spinner.text == "Exam"

        text = self.text_data or self.topic_input.text.strip()
        if not text:
            self.status.text = "⚠ Please enter a topic or upload a file"
            return

        self.quiz = generate_quiz(text, count, level)
        self.index = 0
        self.score = 0

        if self.exam_mode:
            self.time_left = count * 20
            self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        else:
            self.timer_label.text = "🧪 Practice Mode (No timer)"

        self.show_question()

    # ⏱ TIMER
    def update_timer(self, dt):
        self.time_left -= 1
        self.timer_label.text = f"⏳ Time Left: {self.time_left}s"
        if self.time_left <= 0:
            Clock.unschedule(self.timer_event)
            self.finish_exam()

    # ❓ QUESTIONS
    def show_question(self):
        self.options_box.clear_widgets()

        if self.index >= len(self.quiz):
            self.finish_exam()
            return

        q = self.quiz[self.index]
        self.question_label.text = f"Q{self.index+1}. {q['question']}"

        for opt in q["options"]:
            btn = Button(text=opt, size_hint_y=None, height="48dp")
            btn.bind(on_press=self.check_answer)
            self.options_box.add_widget(btn)

    def check_answer(self, btn):
        q = self.quiz[self.index]

        if btn.text == q["answer"]:
            self.score += 1
            btn.background_color = (0.2, 0.8, 0.4, 1)
        else:
            btn.background_color = (0.9, 0.3, 0.3, 1)

        if not self.exam_mode:
            self.question_label.text += "\n\n💡 Explanation:\n" + q["explanation"]

        self.index += 1
        Clock.schedule_once(lambda dt: self.show_question(), 1)

    # 🏁 FINISH
    def finish_exam(self):
        self.question_label.text = (
            f"🎉 Well done!\n\nScore: {self.score}/{len(self.quiz)}\n\n"
            "Keep practicing. Improvement comes with consistency."
        )
        self.options_box.clear_widgets()
        self.save_analytics()

    # 📊 ANALYTICS
    def load_analytics(self):
        self.analytics = {"attempts": 0, "questions": 0, "correct": 0}
        if os.path.exists("analytics.json"):
            with open("analytics.json") as f:
                self.analytics = json.load(f)

    def save_analytics(self):
        self.analytics["attempts"] += 1
        self.analytics["questions"] += len(self.quiz)
        self.analytics["correct"] += self.score
        with open("analytics.json", "w") as f:
            json.dump(self.analytics, f, indent=2)


class QuizApp(App):
    def build(self):
        return QuizLayout()


if __name__ == "__main__":
    QuizApp().run()
