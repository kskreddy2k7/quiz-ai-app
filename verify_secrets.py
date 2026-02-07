import json
import os

try:
    with open('secrets.json', 'r') as f:
        content = f.read()
        print(f"Content length: {len(content)}")
        print(f"First 20 chars: {content[:20]!r}")
        f.seek(0)
        data = json.load(f)
        key = data.get('GEMINI_API_KEY', '')
        print(f"Key loaded: {key[:5]}...{key[-5:] if key else ''}")
except Exception as e:
    print(f"Error loading secrets.json: {e}")
