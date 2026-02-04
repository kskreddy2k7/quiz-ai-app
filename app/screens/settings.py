from __future__ import annotations

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
import os

class SettingsScreen(Screen):
    api_key = StringProperty("")
    status_text = StringProperty("")

    def on_enter(self):
        # Load existing key if possible (masked)
        # Security: We usually shouldn't display it back, but maybe just checking env
        if os.environ.get("OPENAI_API_KEY"):
            self.ids.api_key_input.text = "sk-****"
            self.status_text = "Current Key Active"

    def save_key(self):
        key = self.api_key.strip()
        if key.startswith("sk-") and len(key) > 20:
            os.environ["OPENAI_API_KEY"] = key
            # Persist? Simple app: maybe not needed if we assume env vars set mostly.
            # But for user convenience we can save to storage or .env file locally?
            # For now, memory + verify is good enough for this session.
            app = App.get_running_app()
            app.ai_service.client = None # Force reload
            app._refresh_ai_status()
            self.status_text = "API Key Updated ✅"
        else:
            self.status_text = "Invalid Key Format ❌"
