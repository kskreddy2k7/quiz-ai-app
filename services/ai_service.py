import os
import json
import asyncio
import aiohttp
import google.generativeai as genai
from typing import List, Dict, Any, Optional

class AIService:
    def __init__(self):
        self.cloudflare_api_key = os.getenv("CLOUDFLARE_API_KEY", "")
        self.cloudflare_account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        
        self.has_ai = False
        self.provider = "None"
        self.status = "Offline"
        self.model = None
        self.fallback_models = []
        
        self._initialize_providers()

    def _initialize_providers(self):
        # Refresh from environment
        self.cloudflare_api_key = os.getenv("CLOUDFLARE_API_KEY", "")
        self.cloudflare_account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")

        # Initialize Gemini if key exists
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.has_ai = True
                self.provider = "Gemini"
                self.status = "Online (Gemini)"
            except Exception as e:
                print(f"Gemini init error: {e}")

        if self.cloudflare_api_key and self.cloudflare_account_id:
            self.has_ai = True
            if not self.gemini_api_key:
                self.provider = "Cloudflare"
                self.status = "Online (Cloudflare)"
        
        if not self.gemini_api_key and not (self.cloudflare_api_key and self.cloudflare_account_id):
            self.has_ai = False
            self.provider = "None"
            self.status = "Offline"

    async def generate_with_cloudflare(self, prompt: str) -> str:
        url = f"https://api.cloudflare.com/client/v4/accounts/{self.cloudflare_account_id}/ai/run/@cf/meta/llama-3.3-70b-instruct-fp8-fast"
        headers = {
            "Authorization": f"Bearer {self.cloudflare_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=60) as response:
                if response.status == 200:
                    result = await response.json()
                    res = result.get('result', {})
                    if isinstance(res, dict):
                        return res.get('response') or res.get('text') or res.get('content') or ""
                    elif isinstance(res, str):
                        return res
                    elif isinstance(res, list) and len(res) > 0:
                        first = res[0]
                        if isinstance(first, dict):
                            return first.get('response') or first.get('text') or ""
                        return str(first)
                    raise Exception(f"Unexpected Cloudflare format: {result}")
                else:
                    text = await response.text()
                    raise Exception(f"Cloudflare API error: {response.status} - {text}")

    async def generate_with_gemini(self, prompt: str) -> str:
        if not self.model:
            raise Exception("Gemini model not initialized")
        
        # genai library is synchronous in some parts, but we wrap the call
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: self.model.generate_content(prompt))
        return response.text

    async def generate_quiz(self, prompt: str) -> List[Dict[str, Any]]:
        """Attempt Cloudflare first, then Gemini with error handling and retry logic."""
        text = await self.generate_text(prompt)
        return self._parse_json(text)

    async def generate_text(self, prompt: str) -> str:
        """Generic text generation with fallback."""
        try:
            if self.cloudflare_api_key and self.cloudflare_account_id:
                try:
                    return await self.generate_with_cloudflare(prompt)
                except Exception as e:
                    print(f"Cloudflare failed, falling back to Gemini: {e}")
            
            if self.gemini_api_key:
                return await self.generate_with_gemini(prompt)
                
            raise Exception("No AI provider available or all failed.")
        except Exception as e:
            raise Exception(f"AI Generation Error: {str(e)}")

    def _parse_json(self, text: str) -> List[Dict[str, Any]]:
        cleaned = text.strip()
        if '```json' in cleaned:
            cleaned = cleaned.split('```json')[1].split('```')[0]
        elif '```' in cleaned:
            cleaned = cleaned.split('```')[1].split('```')[0]
            
        data = json.loads(cleaned.strip())
        
        # Standardize format
        if isinstance(data, dict):
            for key in ['questions', 'quiz', 'items']:
                if key in data and isinstance(data[key], list):
                    return data[key]
            if 'prompt' in data and 'choices' in data:
                return [data]
        
        if isinstance(data, list):
            return data
            
        raise ValueError("AI returned invalid JSON structure")

ai_service = AIService()
