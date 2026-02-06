
import os
import time
import sys
# Add project root to path
sys.path.append(os.getcwd())

from app.services.ai_service import AIService
from app.services.quiz_service import QuizService

# Hardcoded key from main.py
API_KEY = "AIzaSyCzGL07JLc003wfbDLmnarcQb-FGMZRn0s"

def test_gemini():
    print("--- Testing Gemini API Connectivity ---")
    ai = AIService(api_key=API_KEY)
    
    if not ai.is_available():
        print("ERROR: AI Service reports unavailable even with key!")
        return

    print("AI Service Initialized. Sending request...")
    
    # Simple synchronous wrapper for testing
    result = {"data": None, "error": None}
    
    def on_success(resp):
        result["data"] = resp
        
    def on_error(err):
        result["error"] = err
        
    ai.run_async(
        prompt="Generate a 1-question Python quiz in JSON format.", 
        system_prompt="You are a quiz bot.",
        on_complete=on_success, 
        on_error=on_error
    )
    
    # Wait for result
    for _ in range(20):
        if result["data"] or result["error"]:
            break
        print(".", end="", flush=True)
        time.sleep(1)
        
    print("\n")
    
    if result["error"]:
        print(f"FAILED: {result['error']}")
    elif result["data"]:
        print(f"SUCCESS: Received response:\n{result['data']}")
    else:
        print("TIMEOUT: No response received.")

if __name__ == "__main__":
    test_gemini()
