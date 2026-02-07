import asyncio
from dotenv import load_dotenv
load_dotenv()
from services.ai_service import ai_service

async def test():
    print("Testing AI Quiz Generation...")
    try:
        prompt = """
    Generate 5 multiple-choice questions about "Python" in English.
    Difficulty: medium (Target Audience: Level 1 Student)
    
    CRITICAL INSTRUCTION: Return ONLY a raw JSON array. Do NOT use Markdown formatting. Do NOT use code blocks.
    Start with [ and end with ].
    
    Structure:
    [
        {{
            "prompt": "Question text",
            "choices": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "The text of the correct option",
            "explanation": "Why correct",
            "wrong_explanations": {{ "Wrong 1": "Reason", "Wrong 2": "Reason" }}
        }}
    ]
    """
        # Call internal method to see raw text first if possible, but generate_quiz calls generate_text then parse
        # Let's call generate_text first to see raw output
        print("--- Sending Request ---")
        raw_text = await ai_service.generate_text(prompt)
        print("--- RAW AI OUTPUT ---")
        print(raw_text)
        print("---------------------")
        
        parsed = ai_service._parse_json(raw_text)
        print("--- PARSED JSON ---")
        print(parsed)
        print("-------------------")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test())
