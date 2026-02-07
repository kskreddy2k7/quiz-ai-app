from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from android.permissions import request_permissions, Permission
from jnius import autoclass

WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
LinearLayout = autoclass('android.widget.LinearLayout')
PythonActivity = autoclass('org.kivy.android.PythonActivity')

class QuizApp(App):
    def build(self):
        # Request internet permission
        request_permissions([Permission.INTERNET])
        
        # Get the current activity
        activity = PythonActivity.mActivity
        
        # Create WebView
        webview = WebView(activity)
        webview.getSettings().setJavaScriptEnabled(True)
        webview.getSettings().setDomStorageEnabled(True)
        webview.setWebViewClient(WebViewClient())
        
        # Load the Render URL
        webview.loadUrl('https://quiz-ai-app-1.onrender.com')
        
        # Set layout parameters
        layout_params = LayoutParams(
            LayoutParams.MATCH_PARENT,
            LayoutParams.MATCH_PARENT
        )
        
        # Add WebView to activity
        activity.addContentView(webview, layout_params)
        
        # Return empty layout (WebView is added directly to activity)
        return BoxLayout()

if __name__ == '__main__':
    QuizApp().run()
