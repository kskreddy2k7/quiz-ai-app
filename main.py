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

from file_reader import read_file
from quiz_generator import generate_quiz

# 🎨 Premium background
Window.clearcolor = (0.96, 0.98, 1, 1)


class QuizLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=22, spacing=16, **kwargs)

        # 🌟 APP HEADER
        self.add_widget(Label(
            text="📚 S Quiz",
            font_size="30sp",
            bold=True,
            color=(0.1, 0.25, 0.6, 1)
        ))

        self.add_widget(Label(
            text="Built with ❤️ by Kranthu\n"
                 "Believe in learning. Practice daily. Win life 🌱",
            font_size="14sp",
            halign="center",
            color=(0.35, 0.35, 0.35, 1)
        ))

        # ✍️ INPUT
        self.topic_input = TextInput(
            hint_text="✏️ Type topic (OR upload file below)",
            size_hint_y=None,
            height="46dp",
            multiline=False
        )
        self.add_widget(self.topic_input)

        self.count_input = TextInput(
            hint_text="🔢 Number of questions (default 5)",
            input_filter="int",
            size_hint_y=None,
            height="46dp"
        )
        self.add_widget(self.count_input)

        self.level_spinner = Spinner(
            text="Easy",
            values=("Easy", "Medium", "Hard"),
            size_hint_y=None,
            height="46dp"
        )
        self.add_widget(self.level_spinner)

        self.mode_spinner = Spinner(
            text="Practice",
            values=("Practice", "Exam"),
            size_hint_y=None,
            height="46dp"
        )
        self.add_widget(self.mode_spinner)

        # 🔘 BUTTONS
        btns = BoxLayout(size_hint_y=None, height="52dp", spacing=12)

        upload_btn = Button(
            text="📂 Browse Study File",
            background_color=(0.2, 0.2, 0.2, 1)
        )
        upload_btn.bind(on_press=self.pick_file)

        start_btn = Button(
            text="🚀 Start Learning",
            background_color=(0.1, 0.55, 0.9, 1)
        )
        start_btn.bind(on_press=self.start_quiz)

        btns.add_widget(upload_btn)
        btns.add_widget(start_btn)
        self.add_widget(btns)

        self.status = Label(text="", font_size="14sp")
        self.add_widget(self.status)

        self.timer_label = Label(text="")
        self.add_widget(self.timer_label)

        self.question_label = Label(
            text="",
            font_size="18sp",
            bold=True,
            halign="left",
            valign="middle"
        )
        self.add_widget(self.question_label)

        self.options_box = BoxLayout(orientation="vertical", spacing=10)
        self.add_widget(self.options_box)

        self.text_data = ""
        self.quiz = []
        self.index = 0
        self.score = 0
        self.exam_mode = False

    # 📂 FILE PICKER (FIXED)
    def pick_file(self, _):
        chooser = FileChooserListView(
            path="/storage/emulated/0/",
            filters=["*.pdf", "*.docx", "*.pptx", "*.txt"],
            show_hidden=False
        )

        popup = Popup(
            title="📂 Select Study Material",
            content=chooser,
            size_hint=(0.95, 0.95)
        )

        def selected(_, files):
            if files:
                self.text_data = read_file(files[0])
                self.status.text = "✅ File loaded successfully"
                popup.dismiss()

        chooser.bind(selection=selected)
        popup.open()

    # ▶ START
    def start_quiz(self, _):
        count = int(self.count_input.text or 5)
        level = self.level_spinner.text.lower()
        self.exam_mode = self.mode_spinner.text == "Exam"

        text = self.text_data or self.topic_input.text.strip()
        if not text:
            self.status.text = "⚠️ Please type a topic or upload a file"
            return

        self.quiz = generate_quiz(text, count, level)
        self.index = 0
        self.score = 0

        if self.exam_mode:
            self.time_left = count * 20
            self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        else:
            self.timer_label.text = "🧪 Practice Mode – Learn freely"

        self.show_question()

    def update_timer(self, dt):
        self.time_left -= 1
        self.timer_label.text = f"⏳ Time Left: {self.time_left}s"
        if self.time_left <= 0:
            Clock.unschedule(self.timer_event)
            self.finish_quiz()

    def show_question(self):
        self.options_box.clear_widgets()

        if self.index >= len(self.quiz):
            self.finish_quiz()
            return

        q = self.quiz[self.index]
        self.question_label.text = q["question"]

        for opt in q["options"]:
            btn = Button(text=opt, size_hint_y=None, height="48dp")
            btn.bind(on_press=self.check_answer)
            self.options_box.add_widget(btn)

    def check_answer(self, btn):
        q = self.quiz[self.index]

        if btn.text == q["answer"]:
            self.score += 1
            btn.background_color = (0.2, 0.85, 0.3, 1)
        else:
            btn.background_color = (0.9, 0.3, 0.3, 1)

        if not self.exam_mode:
            self.question_label.text += "\n\n💡 Explanation:\n" + q["explanation"]

        self.index += 1
        Clock.schedule_once(lambda dt: self.show_question(), 1)

    def finish_quiz(self):
        self.question_label.text = (
            f"🎉 Great job!\n"
            f"Score: {self.score}/{len(self.quiz)}\n\n"
            f"🌱 Keep learning. You are improving every day!"
        )
        self.options_box.clear_widgets()


class QuizApp(App):
    def build(self):
        return QuizLayout()


if __name__ == "__main__":
    QuizApp().run()
