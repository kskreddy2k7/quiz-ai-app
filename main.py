from kivy.core.window import Window
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import random
import threading
import time

# ---------------- THEME ----------------
Window.clearcolor = (0.96, 0.97, 0.98, 1)  # professional light background


# ---------------- SIMULATED ONLINE AI ----------------
def online_ai_generate(topic, count):
    time.sleep(2)

    base_questions = [
        f"{topic} is important in examinations",
        f"{topic} is used in real-world applications",
        f"{topic} improves problem-solving skills",
        f"{topic} is commonly asked in tests",
        f"{topic} requires regular practice",
        f"{topic} questions appear in competitive exams",
        f"{topic} fundamentals are essential",
        f"{topic} concepts should be revised",
        f"{topic} MCQs improve accuracy",
        f"{topic} practice increases scores",
    ]

    selected = random.sample(base_questions, min(count, len(base_questions)))
    quiz = []

    for q in selected:
        correct = q.split()[0]
        options = [correct, "Java", "C++", "JavaScript"]
        random.shuffle(options)

        quiz.append({
            "question": q,
            "options": options,
            "answer": correct
        })

    return quiz


# ---------------- UI ----------------
class QuizUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=25, spacing=18, **kwargs)

        # App Title
        self.title = Label(
            text="S Quiz",
            font_size="26sp",
            bold=True,
            color=(0.1, 0.2, 0.4, 1),
            size_hint_y=None,
            height="50dp"
        )
        self.add_widget(self.title)

        self.subtitle = Label(
            text="Professional Exam Preparation",
            font_size="14sp",
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height="30dp"
        )
        self.add_widget(self.subtitle)

        # Topic Input
        self.topic_input = TextInput(
            hint_text="Subject / Topic (e.g. Python)",
            size_hint_y=None,
            height="45dp",
            multiline=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.add_widget(self.topic_input)

        # Question Count
        self.count_input = TextInput(
            hint_text="Number of Questions",
            input_filter="int",
            size_hint_y=None,
            height="45dp",
            multiline=False
        )
        self.add_widget(self.count_input)

        # Start Button
        self.start_btn = Button(
            text="Start Exam",
            size_hint_y=None,
            height="50dp",
            background_normal="",
            background_color=(0.12, 0.45, 0.85, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        self.start_btn.bind(on_press=self.start_exam)
        self.add_widget(self.start_btn)

        # Status
        self.status = Label(
            text="",
            font_size="13sp",
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height="30dp"
        )
        self.add_widget(self.status)

        # Question Card
        self.question_label = Label(
            text="",
            font_size="18sp",
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height="100dp"
        )
        self.add_widget(self.question_label)

        # Options
        self.options_box = BoxLayout(
            orientation="vertical",
            spacing=12,
            size_hint_y=None
        )
        self.add_widget(self.options_box)

        self.quiz = []
        self.index = 0
        self.score = 0

    def start_exam(self, instance):
        if not self.topic_input.text or not self.count_input.text:
            self.status.text = "Please enter topic and question count"
            return

        self.status.text = "Generating questions..."
        self.start_btn.disabled = True
        threading.Thread(target=self.fetch_quiz).start()

    def fetch_quiz(self):
        self.quiz = online_ai_generate(
            self.topic_input.text,
            int(self.count_input.text)
        )
        Clock.schedule_once(lambda dt: self.start_quiz())

    def start_quiz(self):
        self.start_btn.disabled = False
        self.status.text = ""
        self.index = 0
        self.score = 0
        self.show_question()

    def show_question(self):
        self.options_box.clear_widgets()

        if self.index < len(self.quiz):
            q = self.quiz[self.index]
            self.question_label.text = q["question"]

            for opt in q["options"]:
                btn = Button(
                    text=opt,
                    size_hint_y=None,
                    height="46dp",
                    background_normal="",
                    background_color=(1, 1, 1, 1),
                    color=(0.1, 0.1, 0.1, 1)
                )
                btn.bind(on_press=self.check_answer)
                self.options_box.add_widget(btn)
        else:
            self.question_label.text = (
                f"Exam Completed\nScore: {self.score}/{len(self.quiz)}"
            )

    def check_answer(self, instance):
        if instance.text == self.quiz[self.index]["answer"]:
            self.score += 1

        self.index += 1
        Clock.schedule_once(lambda dt: self.show_question(), 0.3)


class QuizApp(App):
    def build(self):
        return QuizUI()


QuizApp().run()from kivy.core.window import Window
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import random
import threading
import time

# ---------------- THEME ----------------
Window.clearcolor = (0.96, 0.97, 0.98, 1)  # professional light background


# ---------------- SIMULATED ONLINE AI ----------------
def online_ai_generate(topic, count):
    time.sleep(2)

    base_questions = [
        f"{topic} is important in examinations",
        f"{topic} is used in real-world applications",
        f"{topic} improves problem-solving skills",
        f"{topic} is commonly asked in tests",
        f"{topic} requires regular practice",
        f"{topic} questions appear in competitive exams",
        f"{topic} fundamentals are essential",
        f"{topic} concepts should be revised",
        f"{topic} MCQs improve accuracy",
        f"{topic} practice increases scores",
    ]

    selected = random.sample(base_questions, min(count, len(base_questions)))
    quiz = []

    for q in selected:
        correct = q.split()[0]
        options = [correct, "Java", "C++", "JavaScript"]
        random.shuffle(options)

        quiz.append({
            "question": q,
            "options": options,
            "answer": correct
        })

    return quiz


# ---------------- UI ----------------
class QuizUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=25, spacing=18, **kwargs)

        # App Title
        self.title = Label(
            text="S Quiz",
            font_size="26sp",
            bold=True,
            color=(0.1, 0.2, 0.4, 1),
            size_hint_y=None,
            height="50dp"
        )
        self.add_widget(self.title)

        self.subtitle = Label(
            text="Professional Exam Preparation",
            font_size="14sp",
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height="30dp"
        )
        self.add_widget(self.subtitle)

        # Topic Input
        self.topic_input = TextInput(
            hint_text="Subject / Topic (e.g. Python)",
            size_hint_y=None,
            height="45dp",
            multiline=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.add_widget(self.topic_input)

        # Question Count
        self.count_input = TextInput(
            hint_text="Number of Questions",
            input_filter="int",
            size_hint_y=None,
            height="45dp",
            multiline=False
        )
        self.add_widget(self.count_input)

        # Start Button
        self.start_btn = Button(
            text="Start Exam",
            size_hint_y=None,
            height="50dp",
            background_normal="",
            background_color=(0.12, 0.45, 0.85, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        self.start_btn.bind(on_press=self.start_exam)
        self.add_widget(self.start_btn)

        # Status
        self.status = Label(
            text="",
            font_size="13sp",
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height="30dp"
        )
        self.add_widget(self.status)

        # Question Card
        self.question_label = Label(
            text="",
            font_size="18sp",
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height="100dp"
        )
        self.add_widget(self.question_label)

        # Options
        self.options_box = BoxLayout(
            orientation="vertical",
            spacing=12,
            size_hint_y=None
        )
        self.add_widget(self.options_box)

        self.quiz = []
        self.index = 0
        self.score = 0

    def start_exam(self, instance):
        if not self.topic_input.text or not self.count_input.text:
            self.status.text = "Please enter topic and question count"
            return

        self.status.text = "Generating questions..."
        self.start_btn.disabled = True
        threading.Thread(target=self.fetch_quiz).start()

    def fetch_quiz(self):
        self.quiz = online_ai_generate(
            self.topic_input.text,
            int(self.count_input.text)
        )
        Clock.schedule_once(lambda dt: self.start_quiz())

    def start_quiz(self):
        self.start_btn.disabled = False
        self.status.text = ""
        self.index = 0
        self.score = 0
        self.show_question()

    def show_question(self):
        self.options_box.clear_widgets()

        if self.index < len(self.quiz):
            q = self.quiz[self.index]
            self.question_label.text = q["question"]

            for opt in q["options"]:
                btn = Button(
                    text=opt,
                    size_hint_y=None,
                    height="46dp",
                    background_normal="",
                    background_color=(1, 1, 1, 1),
                    color=(0.1, 0.1, 0.1, 1)
                )
                btn.bind(on_press=self.check_answer)
                self.options_box.add_widget(btn)
        else:
            self.question_label.text = (
                f"Exam Completed\nScore: {self.score}/{len(self.quiz)}"
            )

    def check_answer(self, instance):
        if instance.text == self.quiz[self.index]["answer"]:
            self.score += 1

        self.index += 1
        Clock.schedule_once(lambda dt: self.show_question(), 0.3)


class QuizApp(App):
    def build(self):
        return QuizUI()


QuizApp().run()
