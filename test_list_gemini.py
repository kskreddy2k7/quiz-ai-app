
import google.generativeai as genai
import os
from dotenv import load_dotenv
import sys

# Force utf-8 for Windows console
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

key = os.getenv("GEMINI_API_KEY")
if not key:
    print("❌ API Key Missing")
    exit()

print(f"🔑 Using Key: {key[:5]}...{key[-5:]}")

try:
    genai.configure(api_key=key)
    print("\n📋 Fetching Models...")
    
    models = genai.list_models()
    
    found = False
    for m in models:
        print(f"✅ Found: {m.name} | Methods: {m.supported_generation_methods}")
        if 'generateContent' in m.supported_generation_methods:
            found = True
            
    if not found:
        print("❌ No models support generateContent.")
    else:
        print("\n✨ At least one generation model is available.")

except Exception as e:
    print(f"\n❌ Error listing models: {e}")
