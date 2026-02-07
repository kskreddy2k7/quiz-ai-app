import os
import webbrowser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.config import Config

# Set window properties
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'fullscreen', '0')

class QuizApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        info_label = Label(
            text="S Quiz App requires a browser environment.\nPlease click below to open.",
            halign="center",
            valign="middle",
            size_hint=(1, 0.8)
        )
        info_label.bind(size=info_label.setter('text_size'))
        
        open_button = Button(
            text="Open Quiz App",
            size_hint=(1, 0.2),
            background_color=(0.2, 0.6, 1, 1)
        )
        open_button.bind(on_press=self.open_browser)
        
        layout.add_widget(info_label)
        layout.add_widget(open_button)
        return layout
    
    def open_browser(self, instance):
        # In a real app, we would serve the FastAPI app locally.
        # For now, we point to the potentially deployed version or local test.
        # Since we can't easily run the backend on Android without more work,
        # we'll just open a placeholder or the local server URL if the user knows it.
        # Ideally, this should point to the deployed web app URL.
        webbrowser.open('http://127.0.0.1:8000') 
    
    def on_pause(self):
        return True

if __name__ == '__main__':
    QuizApp().run()
