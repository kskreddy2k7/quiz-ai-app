import json
from pathlib import Path


class StorageManager:
    def __init__(self, path: Path):
        self.path = path
        if not path.exists():
            self.path.write_text(
                json.dumps(
                    {
                        "history": [],
                        "scores": [],
                        "streak": 0,
                        "materials": [],
                        "first_launch_shown": False,
                        "last_played_date": "",
                    }
                ),
                encoding="utf-8",
            )

    def load(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
        if not isinstance(data, dict):
            data = {}
        data.setdefault("history", [])
        data.setdefault("scores", [])
        data.setdefault("streak", 0)
        data.setdefault("materials", [])
        data.setdefault("first_launch_shown", False)
        data.setdefault("last_played_date", "")
        return data

    def save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def update_score(self, score: int) -> None:
        data = self.load()
        data["scores"].append(score)
        self.save(data)

    def add_history(self, item: dict) -> None:
        data = self.load()
        data["history"].append(item)
        self.save(data)

    def update_streak(self, date: str) -> int:
        data = self.load()
        if data.get("last_played_date") != date:
            data["streak"] = int(data.get("streak", 0)) + 1
            data["last_played_date"] = date
            self.save(data)
        return int(data.get("streak", 0))

    def add_material(self, item: dict) -> None:
        data = self.load()
        data["materials"].append(item)
        self.save(data)

    def get_materials(self):
        data = self.load()
        return data.get("materials", [])

    def mark_first_launch_shown(self) -> None:
        data = self.load()
        data["first_launch_shown"] = True
        self.save(data)
