from __future__ import annotations

from kivy.properties import ListProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen


class QuizPlayScreen(Screen):
    question_text = StringProperty("")
    option_texts = ListProperty([])
    progress_text = StringProperty("")

    def on_option_texts(self, _instance, options):
        container = self.ids.get("options_container")
        if not container:
            return
        container.clear_widgets()
        for option in options:
            btn = Button(
                text=option,
                size_hint_y=None,
                height=56,
                background_normal="",
                background_color=(0.18, 0.24, 0.32, 1),
                color=(1, 1, 1, 1),
            )
            btn.bind(on_release=lambda btn_instance: self._submit(btn_instance.text))
            container.add_widget(btn)

    def _submit(self, answer: str) -> None:
        from kivy.app import App

        App.get_running_app().submit_answer(answer)
