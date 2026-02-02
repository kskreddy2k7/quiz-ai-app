from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import random

# ---------------- SAMPLE CONTENT ----------------
TEXT_DATA = [
    "Python is a programming language",
    "Kivy is used to build mobile apps",
    "Android apps can be built using Buildozer",
    "Python is popular in AI",
    "MCQ exams help in practice",
    "Practice improves exam performance",
    "Programming improves logical thinking",
    "Python is easy to learn",
    "Mobile apps run on Android",
    "Internet is required for AI apps"
]

# ---------------- QUIZ LOGIC ----------------
def generate_quiz(count):
    questions = []
    selected = random.sample(TEXT_DATA, min(count, len(TEXT_DATA)))

    for text in selected:
        correct = text.split()[0]
        options = [correct, "Java", "C++", "JavaScript"]
        random.shuffle(options)

        questions.append({
            "question": f"Choose the correct first word:\n{text}",
            "options": options,
            "answer": correct
        })
    return questions

# ---------------- UI ----------------
class QuizAppUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=15, **kwargs)

        self.title = Label(text="📝 Exam Practice App", font_size=24)
        self.add_widget(self.title)

        self.input = TextInput(
            hint_text="Enter number of questions (e.g. 5)",
            input_filter="int",
            size_hint=(1, 0.2)
        )
        self.add_widget(self.input)

        self.start_btn = Button(text="Start Exam", size_hint=(1, 0.3))
        self.start_btn.bind(on_press=self.start_exam)
        self.add_widget(self.start_btn)

        self.question_label = Label(text="", font_size=18)
        self.add_widget(self.question_label)

        self.options_box = BoxLayout(orientation="vertical", spacing=10)
        self.add_widget(self.options_box)

        self.quiz = []
        self.index = 0
        self.score = 0

    def start_exam(self, instance):
        if not self.input.text:
            self.question_label.text = "⚠ Enter number of questions"
            return

        count = int(self.input.text)
        self.quiz = generate_quiz(count)
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
        return QuizAppUI()

QuizApp().run()
