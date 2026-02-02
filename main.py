from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import random
import threading
import time

# ---------------- FAKE ONLINE AI (SIMULATION) ----------------
def online_ai_generate(topic, count):
    """
    This simulates an internet AI call.
    Later we replace this with real ChatGPT.
    """
    time.sleep(2)  # simulate network delay

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
            "question": f"Choose the correct word:\n{q}",
            "options": options,
            "answer": correct
        })

    return quiz


# ---------------- UI ----------------
class QuizUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=15, **kwargs)

        self.title = Label(text="📘 AI Exam Practice App", font_size=24)
        self.add_widget(self.title)

        self.topic_input = TextInput(
            hint_text="Enter topic (e.g. Python)",
            size_hint=(1, 0.2)
        )
        self.add_widget(self.topic_input)

        self.count_input = TextInput(
            hint_text="Number of questions (e.g. 5)",
            input_filter="int",
            size_hint=(1, 0.2)
        )
        self.add_widget(self.count_input)

        self.start_btn = Button(text="Generate Exam", size_hint=(1, 0.3))
        self.start_btn.bind(on_press=self.start_exam)
        self.add_widget(self.start_btn)

        self.status = Label(text="", font_size=16)
        self.add_widget(self.status)

        self.question_label = Label(text="", font_size=18)
        self.add_widget(self.question_label)

        self.options_box = BoxLayout(orientation="vertical", spacing=10)
        self.add_widget(self.options_box)

        self.quiz = []
        self.index = 0
        self.score = 0

    def start_exam(self, instance):
        if not self.topic_input.text or not self.count_input.text:
            self.status.text = "⚠ Enter topic and question count"
            return

        self.status.text = "🌐 Generating questions online..."
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
                btn = Button(text=opt)
                btn.bind(on_press=self.check_answer)
                self.options_box.add_widget(btn)
        else:
            self.question_label.text = f"✅ Exam Finished!\nScore: {self.score}/{len(self.quiz)}"

    def check_answer(self, instance):
        if instance.text == self.quiz[self.index]["answer"]:
            self.score += 1

        self.index += 1
        self.show_question()


class QuizApp(App):
    def build(self):
        return QuizUI()


QuizApp().run()
