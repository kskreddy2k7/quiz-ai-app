from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class StorageService:
    """
    Manages local data persistence for user progress, settings, and cache.
    """
    def __init__(self, filename: str = "quiz_data.json"):
        # Helper to get writable path even on Android
        from kivy.app import App
        try:
            # Safe writable path for both Desktop and Android
            app = App.get_running_app()
            if app and app.user_data_dir:
                root = Path(app.user_data_dir)
            else:
                # Fallback if app not yet running
                from kivy.utils import platform
                if platform == 'android':
                    root = Path("/data/data/org.sai.squiz/files")
                else:
                    root = Path(".")
        except Exception:
            root = Path(".")

        root.mkdir(parents=True, exist_ok=True)
        self.path = root / filename

        self._init_storage()

    def _init_storage(self):
        if not self.path.exists():
            self._write_default_data()

    def _write_default_data(self):
        default_data = {
            "history": [],
            "scores": [],
            "streak": 0,
            "materials": [],
            "first_launch_shown": False,
            "last_played_date": "",
            "settings": {
                "theme": "dark",
                "sound_enabled": True,
                "api_key": ""
            }
        }
        self.save(default_data)

    def load(self) -> Dict[str, Any]:
        try:
            text = self.path.read_text(encoding="utf-8")
            if not text.strip():
                return self._recover_storage()
            data = json.loads(text)
        except (json.JSONDecodeError, OSError):
            return self._recover_storage()
            
        if not isinstance(data, dict):
            return self._recover_storage()
            
        return data

    def _recover_storage(self) -> Dict[str, Any]:
        """Reset storage if corrupted."""
        self._write_default_data()
        return self.load()

    def save(self, data: Dict[str, Any]) -> None:
        try:
            self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except OSError as e:
            print(f"Error saving data: {e}")

    # --- Convenience Methods ---

    def update_score(self, score: int) -> None:
        data = self.load()
        data.setdefault("scores", []).append(score)
        self.save(data)

    def add_history(self, item: dict) -> None:
        data = self.load()
        data.setdefault("history", []).append(item)
        self.save(data)

    def update_streak(self, date: str) -> int:
        data = self.load()
        if data.get("last_played_date") != date:
            current_streak = int(data.get("streak", 0))
            # Logic could be improved to check if consecutive days
            # For now, simplistic increment if date changed
            data["streak"] = current_streak + 1
            data["last_played_date"] = date
            self.save(data)
        return int(data.get("streak", 0))

    def add_material(self, item: dict) -> None:
        data = self.load()
        data.setdefault("materials", []).append(item)
        self.save(data)

    def get_materials(self) -> List[dict]:
        return self.load().get("materials", [])

    def mark_first_launch_shown(self) -> None:
        data = self.load()
        data["first_launch_shown"] = True
        self.save(data)

    def get_backend_url(self) -> str:
        return self.load().get("settings", {}).get("backend_url", "")

    def save_backend_url(self, url: str) -> None:
        data = self.load()
        if "settings" not in data:
            data["settings"] = {}
        data["settings"]["backend_url"] = url
        self.save(data)
