from __future__ import annotations

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
import os

class SettingsScreen(Screen):
    backend_url = StringProperty("http://127.0.0.1:8001")
    status_text = StringProperty("")

    def on_enter(self):
        # Load existing url
        app = App.get_running_app()
        self.backend_url = app.ai_service.backend_url
        self.ids.backend_url_input.text = self.backend_url
        
        # Check status
        if app.ai_service.is_available():
            self.status_text = "Connected ✅"
        else:
            self.status_text = "Not Connected ❌"

    def save_backend(self):
        url = self.backend_url.strip().rstrip("/")
        if not url.startswith("http"):
            self.status_text = "Invalid URL (must start with http) ❌"
            return
            
        app = App.get_running_app()
        app.ai_service.backend_url = url
        app.storage_service.save_backend_url(url)
        
        # Check connection
        if app.ai_service.is_available():
            self.status_text = "Connected & Saved ✅"
        else:
            self.status_text = "Saved, but Offline ⚠️"
