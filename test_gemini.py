
import os
import google.generativeai as genai
from dotenv import load_dotenv
import sys

# Force utf-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

KEY = os.getenv("GEMINI_API_KEY")

def main():
    print("Testing Gemini Models Loop (ASCII)...")
    if not KEY:
        print("No Key")
        return

    try:
        genai.configure(api_key=KEY)
        
        candidates = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "gemini-pro"
        ]
        
        for model_name in candidates:
            print(f"\n--- Testing {model_name} ---")
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello")
                print(f"[SUCCESS]: {model_name}")
                print(f"Response: {response.text}")
                # We stop after first success? No, let's test all to see options.
            except Exception as e:
                print(f"[FAILED]: {e}")
                
    except Exception as e:
        print("Fatal Error:", e)

if __name__ == "__main__":
    main()
