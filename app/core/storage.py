import json
from pathlib import Path


class StorageManager:
    def __init__(self, path: Path):
        self.path = path
        if not path.exists():
            self.path.write_text(json.dumps({"history": [], "scores": [], "streak": 0}))

    def load(self):
        return json.loads(self.path.read_text())

    def update_score(self, score):
        data = self.load()
        data["scores"].append(score)
        self.path.write_text(json.dumps(data, indent=2))

    def add_history(self, item):
        data = self.load()
        data["history"].append(item)
        self.path.write_text(json.dumps(data, indent=2))

    def update_streak(self, date):
        data = self.load()
        data["streak"] += 1
        self.path.write_text(json.dumps(data, indent=2))
        return data["streak"]
