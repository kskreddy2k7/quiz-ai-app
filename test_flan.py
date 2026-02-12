
import asyncio
import aiohttp
import os
import json
from dotenv import load_dotenv

load_dotenv()

HF_KEY = os.getenv("HUGGINGFACE_API_KEY")

async def test_endpoint(model, base_url, prompt):
    url = base_url.format(model=model)
    print(f"\n--- Testing url: {url} ---")
    
    headers = {"Authorization": f"Bearer {HF_KEY}", "Content-Type": "application/json"}
    
    payload = {"inputs": prompt, "parameters": {"max_length": 50, "temperature": 0.1}}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=payload) as resp:
                print(f"Status: {resp.status}")
                if resp.status == 200:
                    data = await resp.json()
                    print("SUCCESS:", json.dumps(data)[:200])
                    return True
                else:
                    print("Error:", (await resp.text())[:200])
                    return False
        except Exception as e:
            print(f"Exception: {e}")
            return False

async def main():
    model = "google/flan-t5-large"
    prompt = "Translate English to German: Hello world"
    
    endpoints = [
        "https://api-inference.huggingface.co/models/{model}",
        "https://router.huggingface.co/models/{model}",
        "https://router.huggingface.co/hf-inference/models/{model}",
        "https://router.huggingface.co/{model}",
        "https://router.huggingface.co/v1/models/{model}"
    ]
    
    for ep in endpoints:
        success = await test_endpoint(model, ep, prompt)
        if success:
            print(f"\n✅ FOUND WORKING ENDPOINT: {ep}")
            break

if __name__ == "__main__":
    asyncio.run(main())
