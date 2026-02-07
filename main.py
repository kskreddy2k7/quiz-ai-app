import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.webview import WebView
from kivy.config import Config

# Set window properties
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'fullscreen', '0')

class QuizApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        # Create webview to load the local web app
        webview = WebView()
        
        # Check if we're running in debug mode or production
        if os.environ.get('QUIZ_DEBUG'):
            # Load from local server in debug mode
            webview.load_url('http://localhost:8000')
        else:
            # Load from packaged files in production
            webview.load_html_from_file('static/index.html')
        
        layout.add_widget(webview)
        return layout
    
    def on_pause(self):
        # Handle app pause (phone call, etc.)
        return True

if __name__ == '__main__':
    QuizApp().run()
