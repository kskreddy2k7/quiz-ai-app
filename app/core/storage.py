import json
from pathlib import Path


class StorageManager:
    def __init__(self, path: Path):
        self.path = path
        if not path.exists():
            self.path.write_text(
                json.dumps({"history": [], "scores": [], "streak": 0, "materials": []})
            )

    def load(self):
        try:
            data = json.loads(self.path.read_text())
        except (json.JSONDecodeError, OSError):
            data = {}
        if not isinstance(data, dict):
            data = {}
        data.setdefault("history", [])
        data.setdefault("scores", [])
        data.setdefault("streak", 0)
        data.setdefault("materials", [])
        return data

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

    def add_material(self, item):
        data = self.load()
        data["materials"].append(item)
        self.path.write_text(json.dumps(data, indent=2))

    def get_materials(self):
        data = self.load()
        return data.get("materials", [])
