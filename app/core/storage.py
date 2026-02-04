from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class StorageManager:
    def __init__(self, path: Path) -> None:
        self.path = path
        if not self.path.exists():
            self._write({"scores": [], "history": [], "streak": 0, "last_date": "", "materials": []})

    def _write(self, data: Dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load(self) -> Dict:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def update_score(self, score: int) -> None:
        data = self.load()
        data.setdefault("scores", []).append(score)
        self._write(data)

    def add_history(self, entry: Dict) -> None:
        data = self.load()
        data.setdefault("history", []).append(entry)
        self._write(data)

    def update_streak(self, today: str) -> int:
        data = self.load()
        last_date = data.get("last_date", "")
        streak = data.get("streak", 0)
        if last_date != today:
            streak = streak + 1 if last_date else 1
        data["last_date"] = today
        data["streak"] = streak
        self._write(data)
        return streak

    def add_material(self, entry: Dict) -> None:
        data = self.load()
        data.setdefault("materials", []).append(entry)
        self._write(data)

    def get_materials(self) -> List[Dict]:
        data = self.load()
        return data.get("materials", [])
