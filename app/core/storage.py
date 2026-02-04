from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_DATA = {
    "history": [],
    "streak": 0,
    "last_played": None,
    "scores": [],
}


@dataclass
class StorageManager:
    path: Path
    _cache: Dict[str, Any] = field(default_factory=dict)

    def load(self) -> Dict[str, Any]:
        if self._cache:
            return self._cache
        if not self.path.exists():
            self._cache = DEFAULT_DATA.copy()
            return self._cache
        try:
            self._cache = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            self._cache = DEFAULT_DATA.copy()
        return self._cache

    def save(self, data: Dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self._cache = data

    def add_history(self, entry: Dict[str, Any]) -> None:
        data = self.load()
        history: List[Dict[str, Any]] = data.get("history", [])
        history.insert(0, entry)
        data["history"] = history[:30]
        self.save(data)

    def update_score(self, score: int) -> None:
        data = self.load()
        scores: List[int] = data.get("scores", [])
        scores.append(score)
        data["scores"] = scores[-30:]
        self.save(data)

    def update_streak(self, today: str) -> int:
        data = self.load()
        last_played = data.get("last_played")
        streak = data.get("streak", 0)
        if last_played == today:
            return streak
        if last_played is None:
            streak = 1
        else:
            streak = streak + 1 if last_played < today else 1
        data["last_played"] = today
        data["streak"] = streak
        self.save(data)
        return streak
