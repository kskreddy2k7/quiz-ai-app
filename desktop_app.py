"""
Quiz AI Academy - PREMIUM DESKTOP APP
Beautiful animated interface with all features
"""

import webview
import threading
from app import app, HAS_GEMINI
import time

def start_flask():
    """Start Flask server in background"""
    app.run(debug=False, port=5002, use_reloader=False)

def create_window():
    """Create premium desktop window"""
    time.sleep(2)
    
    window = webview.create_window(
        title='S Quiz by Sai - Premium Edition',
        url='http://localhost:5002',
        width=1400,
        height=900,
        resizable=True,
        fullscreen=False,
        on_top=True,
        min_size=(1000, 700)
    )
    
    webview.start()

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🌟" + " "*20 + "QUIZ AI ACADEMY - PREMIUM" + " "*20 + "🌟")
    print("="*70)
    print(f"✅ AI Status: {'Online' if HAS_GEMINI else 'Offline'}")
    print("\n✨ Premium Features:")
    print("   🎯 Custom question count (1-100)")
    print("   🎨 Beautiful animated gradient UI")
    print("   💡 Motivational quotes")
    print("   😊 Enhanced emojis throughout")
    print("   📂 File upload (PDF/DOCX/TXT)")
    print("   👨‍🏫 Teacher assistance tools")
    print("   💬 AI help system")
    print("   🌐 Multi-language support")
    print("\n📱 Starting premium desktop application...")
    print("="*70 + "\n")
    
    # Start Flask in background
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Create and show window
    create_window()
