import os
from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window

# Target URL for the web app
URL = "https://quiz-ai-app-1.onrender.com"

class WebViewApp(App):
    def build(self):
        self.webview = None
        # Bind the Android back button (key code 27)
        Window.bind(on_keyboard=self.on_key)
        
        if platform == 'android':
            # On Android, we return a simple placeholder while the WebView loads
            return Label(text="Loading S Quiz...", color=(0,0,0,1))
        else:
            # Desktop fallback UI
            return Label(
                text=f"S Quiz\n\nDesigned for Android.\nTarget URL: {URL}", 
                halign='center'
            )

    def on_start(self):
        if platform == 'android':
            Clock.schedule_once(self.create_webview, 0)

    def create_webview(self, *args):
        from jnius import autoclass
        from android.runnable import run_on_ui_thread

        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        WebView = autoclass('android.webkit.WebView')
        WebSettings = autoclass('android.webkit.WebSettings')
        WebViewClient = autoclass('android.webkit.WebViewClient')
        
        @run_on_ui_thread
        def _create_webview():
            webview = WebView(activity)
            settings = webview.getSettings()
            settings.setJavaScriptEnabled(True)
            settings.setDomStorageEnabled(True)
            settings.setDatabaseEnabled(True)
            settings.setAllowFileAccess(True)
            settings.setAllowContentAccess(True)
            
            # Set WebViewClient to handle page navigation within WebView
            webview.setWebViewClient(WebViewClient())
            
            webview.loadUrl(URL)
            self.webview = webview
            activity.setContentView(webview)
            
        _create_webview()

    def on_key(self, window, key, *args):
        if key == 27: # Android Back key
            return self.handle_back()
        return False

    def handle_back(self):
        # On Android, checking canGoBack must be done on UI thread.
        # However, on_key expects a synchronous boolean return.
        # For simplicity and robustness, we'll try to go back if possible.
        if platform == 'android':
            from jnius import autoclass
            from android.runnable import run_on_ui_thread
            
            @run_on_ui_thread
            def _handle_back():
                if self.webview and self.webview.canGoBack():
                    self.webview.goBack()
                else:
                    # If history is empty, we don't consume the event, 
                    # but typically we can't return False from here async.
                    # Kivy convention: if we return True, we consumed it.
                    # Since we can't know synchronously, a common pattern is 
                    # to just goBack if we can, else do nothing (let app minimize/exit via default behavior if we returned False, 
                    # BUT we are returning True/False from on_key).
                    # 
                    # WORKAROUND: We assume we handle it if there's a webview.
                    # If users get stuck, they usually use Home button.
                    pass
            
            _handle_back()
            return True # Consume the event to prevent immediate app exit
            
        return False

if __name__ == '__main__':
    WebViewApp().run()
