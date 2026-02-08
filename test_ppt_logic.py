import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from services.ai_service import ai_service

async def test_gen():
    print("Testing Presentation Generation...")
    
    # Check if AI is available
    if not ai_service.has_ai:
        print("⚠️ AI not configured. Skipping test.")
        return

    topic = "The Future of Artificial Intelligence"
    try:
        content = await ai_service.generate_presentation_content(
            topic=topic,
            num_slides=5,
            language="English",
            theme="Cyberpunk",
            tone="Futuristic"
        )
        
        if "Key Concepts" in [s.get('title') for s in content.get("slides", [])]:
            print("\n⚠️  WARNING: Fallback content detected!")
        else:
            print("\n✨ AI Generated Content Verified!")

        print(f"Title: {content.get('title')}")
        print(f"Theme: {content.get('theme')}")
        print(f"Font: {content.get('font')}")
        print(f"Slides: {len(content.get('slides', []))}")
        
        # Verify structure
        for i, slide in enumerate(content.get("slides", [])):
            print(f"  Slide {i+1}: {slide.get('title')} ({len(slide.get('content', []))} points)")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_gen())
