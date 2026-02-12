import asyncio
import os
import sys
from dotenv import load_dotenv

# Add current dir to path to import services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load env
load_dotenv()

async def main():
    print("=== AI DIAGNOSTICS V2 ===")
    
    try:
        print("Importing AI Service...")
        from services.ai_service import ai_service
        print(f"Service Loaded. Status: {ai_service.status}")
        
        print(f"Gemini Key Present: {bool(ai_service.gemini_api_key)}")
        print(f"HF Key Present: {bool(ai_service.huggingface_api_key)}")
        print(f"HF URL: {ai_service.huggingface_api_key and 'https://router.huggingface.co/models'}")
        
        print("\n--- Testing Gemini ---")
        try:
            res = await ai_service.generate_with_gemini("Test: Reply 'OK'")
            print(f"✅ Gemini: SUCCESS - {res.strip()[:20]}")
        except Exception as e:
            print(f"❌ Gemini: FAILED - {e}")

        print("\n--- Testing Hugging Face ---")
        try:
            # We must use proper model name logic, but let's test the default
            res = await ai_service.generate_with_huggingface("Test: Reply 'OK'")
            print(f"✅ HF: SUCCESS - {res.strip()[:20]}")
        except Exception as e:
            print(f"❌ HF: FAILED - {e}")

    except ImportError as e:
        print(f"CRITICAL IMPORT ERROR: {e}")
    except Exception as e:
        print(f"CRITICAL SCRIPT ERROR: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
