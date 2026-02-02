from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
import random

# ---------------- BUILT-IN CONTENT ----------------
TEXT_DATA = """
Python is a programming language.
It is widely used in artificial intelligence.
Kivy is a Python framework for mobile apps.
Android apps can be built using Buildozer.
Python is easy to learn and powerful.
"""

# ---------------- QUIZ LOGIC ----------------
def generate_quiz(text):
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 5]
    quiz = []

    for s in sentences:
        words = s.split()
        answer = words[0]

        options = [
            answer,
            "Java",
            "C++",
            "JavaScript"
        ]
        random.shuffle(options)

        quiz.append({
            "question": f"What is the first word of:\n\n{s}?",
            "options": options,
            "answer": answer
        })

    return quiz


# ---------------- UI ----------------
class QuizLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.question_label = Label(text="Press Start Quiz", font_size=18)
        self.add_widget(self.question_label)

        self.options_box = BoxLayout(orientation="vertical")
        self.add_widget(self.options_box)

        self.start_btn = Button(text="Start Quiz", size_hint=(1, 0.2))
        self.start_btn.bind(on_press=self.start_quiz)
        self.add_widget(self.start_btn)

        self.quiz = []
        self.index = 0
        self.score = 0

    def start_quiz(self, instance):
        self.quiz = generate_quiz(TEXT_DATA)
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
            self.question_label.text = f"🎉 Quiz Finished!\nScore: {self.score}/{len(self.quiz)}"

    def check_answer(self, instance):
        if instance.text == self.quiz[self.index]["answer"]:
            self.score += 1

        self.index += 1
        self.show_question()


class QuizApp(App):
    def build(self):
        return QuizLayout()


QuizApp().run()
