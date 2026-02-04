from __future__ import annotations

import json
from pathlib import Path
from typing import List

from kivy.properties import ListProperty, StringProperty
from kivy.uix.screenmanager import Screen


class QuizSetupScreen(Screen):
    subjects = ListProperty([])
    topics = ListProperty([])
    difficulties = ListProperty(["easy", "medium", "hard"])
    selected_subject = StringProperty("")
    selected_topic = StringProperty("")
    selected_difficulty = StringProperty("easy")

    def load_subjects(self, path: Path) -> None:
        if not path.exists():
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        self.subjects = [item["name"] for item in data.get("subjects", [])]
        self.difficulties = data.get("difficulties", self.difficulties)
        if self.subjects:
            self.selected_subject = self.subjects[0]
            self._update_topics(data)

    def _update_topics(self, data: dict) -> None:
        for item in data.get("subjects", []):
            if item["name"] == self.selected_subject:
                self.topics = item.get("topics", [])
                if self.topics:
                    self.selected_topic = self.topics[0]
                return
        self.topics = []
        self.selected_topic = ""

    def set_subject(self, subject: str, path: Path) -> None:
        self.selected_subject = subject
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            self._update_topics(data)

    def set_topic(self, topic: str) -> None:
        self.selected_topic = topic

    def set_difficulty(self, difficulty: str) -> None:
        self.selected_difficulty = difficulty
