from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
import random


def generate_ai_quiz(text):
    lines = [l.strip() for l in text.split('.') if len(l.strip()) > 20]
    quiz = []

    for line in lines[:5]:
        words = line.split()
        answer = " ".join(words[-3:])
        options = [
            answer,
            "Not related",
            "None of the above",
            words[0]
        ]
        random.shuffle(options)

        quiz.append({
            "question": f"What is this sentence mainly about?\n\n{line}",
            "options": options,
            "answer": answer
        })
    return quiz


class QuizLayout(BoxLayout):
    quiz = []
    index = 0
    score = 0

    def show_question(self):
        if self.index < len(self.quiz):
            q = self.quiz[self.index]
            self.ids.question.text = q["question"]
            self.ids.options.clear_widgets()

            for option in q["options"]:
                btn = Button(text=option, size_hint_y=None, height=48)
                btn.bind(on_press=self.check_answer)
                self.ids.options.add_widget(btn)
        else:
            self.ids.question.text = f"Quiz Finished!\nScore: {self.score}/{len(self.quiz)}"
            self.ids.options.clear_widgets()

    def check_answer(self, instance):
        if instance.text == self.quiz[self.index]["answer"]:
            self.score += 1
        self.index += 1
        self.show_question()


class QuizApp(App):
    text_data = ""

    def build(self):
        self.layout = QuizLayout()
        return self.layout

    def pick_file(self):
        chooser = FileChooserListView(path="/sdcard/Download")
        popup = Popup(title="Select Text File",
                      content=chooser,
                      size_hint=(0.9, 0.9))

        def on_select(instance, selection):
            if selection:
                try:
                    with open(selection[0], 'r', encoding='utf-8') as f:
                        self.text_data = f.read()
                    popup.dismiss()
                except:
                    popup.dismiss()

        chooser.bind(selection=on_select)
        popup.open()

    def start_quiz(self):
        if self.text_data:
            self.layout.quiz = generate_ai_quiz(self.text_data)
            self.layout.index = 0
            self.layout.score = 0
            self.layout.show_question()
        else:
            self.layout.ids.question.text = "Please select a text file first."


QuizApp().run()
