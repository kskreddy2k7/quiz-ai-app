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
        app = App.get_running_app()
        stored_key = app.storage_service.get_api_key()
        env_key = os.environ.get("GEMINI_API_KEY")
        
        current_key = stored_key or env_key
        if current_key:
            self.ids.api_key_input.text = f"{current_key[:4]}...{current_key[-4:]}"
            self.status_text = "Current Key Active"

    def save_key(self):
        key = self.api_key.strip()
        # Gemini keys usually start with AIza and are approx 39 chars
        if key.startswith("AIza") and len(key) > 30:
            os.environ["GEMINI_API_KEY"] = key
            
            app = App.get_running_app()
            app.storage_service.save_api_key(key)
            app.ai_service.set_api_key(key)
            app._refresh_ai_status()
            
            self.status_text = "API Key Saved ✅"
        else:
            self.status_text = "Invalid Gemini Key (starts with AIza) ❌"
