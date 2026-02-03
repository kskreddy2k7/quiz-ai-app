from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window


class QuizAiMobileApp(App):
    def build(self):
        Window.clearcolor = (0.96, 0.98, 1, 1)
        root = BoxLayout(orientation="vertical", padding=24, spacing=16)

        root.add_widget(
            Label(
                text="QuizAI Academy 📘",
                font_size="28sp",
                color=(0.18, 0.22, 0.55, 1),
                size_hint_y=None,
                height=48,
            )
        )
        root.add_widget(
            Label(
                text=(
                    "Your AI-powered learning hub is ready!\n"
                    "Generate quizzes, chat with the tutor, and learn smarter."
                ),
                font_size="16sp",
                color=(0.35, 0.35, 0.35, 1),
                halign="center",
            )
        )

        root.add_widget(Widget())

        root.add_widget(
            Button(
                text="Start Learning ✨",
                size_hint_y=None,
                height=52,
                background_color=(0.31, 0.28, 0.9, 1),
            )
        )
        return root


if __name__ == "__main__":
    QuizAiMobileApp().run()
