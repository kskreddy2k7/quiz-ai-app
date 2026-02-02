from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label

from android.permissions import request_permissions, Permission


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
                btn = Button(text=option)
                btn.bind(on_press=self.check_answer)
                self.ids.options.add_widget(btn)
        else:
            self.ids.question.text = f"Quiz Finished! Score: {self.score}/{len(self.quiz)}"
            self.ids.options.clear_widgets()

    def check_answer(self, instance):
        correct = self.quiz[self.index]["answer"]
        if instance.text == correct:
            self.score += 1
        self.index += 1
        self.show_question()


class QuizApp(App):
    text_data = ""

    def build(self):
        # Ask Android for file permission at runtime
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])

        self.layout = QuizLayout()
        return self.layout

    def pick_file(self):
        chooser = FileChooserListView(path="/sdcard/Download")
        popup = Popup(
            title="Select File",
            content=chooser,
            size_hint=(0.9, 0.9)
        )

        def on_select(instance, selection):
            if selection:
                print("Selected file:", selection[0])
                popup.dismiss()

        chooser.bind(selection=on_select)
        popup.open()

    def start_quiz(self):
        self.layout.ids.question.text = "Quiz logic will be added here"


QuizApp().run()
