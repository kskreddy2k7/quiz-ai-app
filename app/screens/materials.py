from __future__ import annotations

import importlib.util
from pathlib import Path

from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen


class MaterialsScreen(Screen):
    materials_text = StringProperty("")
    status_text = StringProperty("")

    def add_material(self) -> None:
        if not importlib.util.find_spec("plyer"):
            self.status_text = "File picker unavailable on this device."
            return
        from plyer import filechooser

        def handle_selection(selection):
            if not selection:
                self.status_text = "No file selected."
                return
            path = Path(selection[0])
            label = path.stem
            from kivy.app import App

            App.get_running_app().add_material_entry(label, str(path))
            self.status_text = f"Saved: {label}"

        filechooser.open_file(on_selection=handle_selection)
