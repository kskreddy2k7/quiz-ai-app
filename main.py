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

# ---------------- APP THEME ----------------
Window.clearcolor = (0.95, 0.97, 1, 1)  # light modern background


# ---------------- FAKE ONLINE AI (SIMULATION) ----------------
def online_ai_generate(topic, count):
    time.sleep(2)  # simulate internet delay

    base_questions = [
        f"{topic} is important in exams",
        f"{topic} is used in real-world applications",
        f"{topic} improves problem solving",
        f"{topic} is commonly asked in tests",
        f"{topic} requires regular practice",
        f"{topic} questions appear in competitive exams",
        f"{topic} fundamentals are essential",
        f"{topic} concepts should be revised",
        f"{topic} MCQs help learning",
        f"{topic} practice improves score",
    ]

    selected = random.sample(base_questions, min(count, len(base_questions)))
    quiz = []

    for q in selected:
        correct = q.split()[0]
        options = [correct, "Java", "C++", "JavaScript"]
        random.shuffle(options)

        quiz.append({
            "question": f"[b]{q}[/b]",
            "options": options,
            "answer": correct
        })

    return quiz


# ---------------- UI ----------------
class QuizUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=15, **kwargs)

        # Header
        self.title = Label(
            text="[b]S Quiz – Smart Exam Prep[/b]",
            markup=True,
            font_size="24sp",
            color=(0.1, 0.3, 0.7, 1),
            size_hint_y=None,
            height="50dp"
        )
        self.add_widget(self.title)

        # Topic input
        self.topic_input = TextInput(
            hint_text="Enter topic (e.g. Python)",
            size_hint_y=None,
            height="45dp",
            multiline=False
        )
        self.add_widget(self.topic_input)

        # Count input
        self.count_input = TextInput(
            hint_text="Number of questions (e.g. 5)",
            input_filter="int",
            size_hint_y=None,
            height="45dp",
            multiline=False
        )
        self.add_widget(self.count_input)

        # Start button
        self.start_btn = Button(
            text="Generate Exam",
            size_hint_y=None,
            height="50dp",
            background_normal="",
            background_color=(0.15, 0.55, 0.95, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        self.start_btn.bind(on_press=self.start_exam)
        self.add_widget(self.start_btn)

        # Status
        self.status = Label(text="", font_size="14sp")
        self.add_widget(self.status)

        # Question
        self.question_label = Label(
            text="",
            markup=True,
            font_size="18sp",
            size_hint_y=None,
            height="100dp",
            color=(0, 0, 0, 1)
        )
        self.add_widget(self.question_label)

        # Options
        self.options_box = BoxLayout(orientation="vertical", spacing=10)
        self.add_widget(self.options_box)

        self.quiz = []
        self.index = 0
        self.score = 0

    def start_exam(self, instance):
        if not self.topic_input.text or not self.count_input.text:
            self.status.text = "⚠ Please enter topic and number of questions"
            return

        self.status.text = "🌐 Generating questions..."
        self.start_btn.disabled = True
        threading.Thread(target=self.fetch_quiz).start()

    def fetch_quiz(self):
        topic = self.topic_input.text
        count = int(self.count_input.text)
        self.quiz = online_ai_generate(topic, count)
        Clock.schedule_once(lambda dt: self.start_quiz_ui())

    def start_quiz_ui(self):
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
                    height="48dp",
                    background_normal="",
                    background_color=(0.2, 0.6, 1, 1),
                    color=(1, 1, 1, 1),
                    bold=True
                )
                btn.bind(on_press=self.check_answer)
                self.options_box.add_widget(btn)
        else:
            self.question_label.text = (
                f"[b]Exam Finished![/b]\nScore: {self.score}/{len(self.quiz)}"
            )

    def check_answer(self, instance):
        if instance.text == self.quiz[self.index]["answer"]:
            self.score += 1

        self.index += 1
        Clock.schedule_once(lambda dt: self.show_question(), 0.25)


class QuizApp(App):
    def build(self):
        return QuizUI()


QuizApp().run()
