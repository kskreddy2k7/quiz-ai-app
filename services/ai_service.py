import os
import json
import asyncio
import aiohttp
import google.generativeai as genai
import ast
import re
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
        self.cloudflare_api_key = os.getenv("CLOUDFLARE_API_KEY", "").split('#')[0].strip().strip('"')
        self.cloudflare_account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").split('#')[0].strip().strip('"')
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "").split('#')[0].strip().strip('"')

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
                        val = res.get('response') or res.get('text') or res.get('content') or ""
                        return str(val) if not isinstance(val, (str, bytes)) else val
                    elif isinstance(res, str):
                        return res
                    elif isinstance(res, list) and len(res) > 0:
                        first = res[0]
                        if isinstance(first, dict):
                            val = first.get('response') or first.get('text') or ""
                            return str(val) if not isinstance(val, (str, bytes)) else val
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
        last_error = None
        for attempt in range(3): # Retry up to 3 times
            try:
                text = await self.generate_text(prompt)
                return self._parse_json(text)
            except Exception as e:
                print(f"Attempt {attempt+1} failed: {e}")
                last_error = e
                # Wait briefly before retrying
                await asyncio.sleep(1)
        
        raise last_error or Exception("Failed to generate quiz after 3 attempts")

    async def chat_with_teacher(self, history: List[Dict[str, str]], message: str) -> str:
        """Chat with the Friendly Teacher persona."""
        system_prompt = (
            "You are a friendly, encouraging, and patient teacher. "
            "Your goal is to help students understand concepts deeply. "
            "Use simple language, analogies, and ASCII charts/diagrams where helpful. "
            "Never give just the answer; explain the 'why'. "
            "Keep responses concise but helpful."
        )
        # Construct full prompt (simple concatenation for now, can be improved)
        full_prompt = f"System: {system_prompt}\n\n"
        for msg in history:
            # Ensure role is mapped correctly
            role = "Teacher" if msg['role'] == "model" or msg['role'] == "assistant" else "Student"
            full_prompt += f"{role}: {msg['content']}\n"
        full_prompt += f"Student: {message}\nTeacher:"
        
        return await self.generate_text(full_prompt)

    async def explain_concept(self, text: str, context: Optional[str] = None) -> str:
        """Provide a deep, step-by-step explanation."""
        prompt = (
            f"Act as a friendly teacher. Explain the following concept/question step-by-step:\n"
            f"'{text}'\n"
        )
        if context:
            prompt += f"\nContext from file/quiz: {context}\n"
            
        prompt += "\nUse an analogy and if possible, a small ASCII diagram/chart to visualize it."
        return await self.generate_text(prompt)

    async def summarize_text(self, text: str) -> str:
        """Generate a concise summary of the text."""
        prompt = (
            f"Summarize the following text in 3-4 bullet points, capturing the key concepts:\n"
            f"'{text[:10000]}'\n" # Limit input to avoid overload
            f"\nSummary:"
        )
        return await self.generate_text(prompt)

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

    def _parse_json(self, text: Any) -> List[Dict[str, Any]]:
        if isinstance(text, list):
            return text
        if isinstance(text, dict):
            data = text
        else:
            cleaned = str(text).strip()
            if '```json' in cleaned:
                cleaned = cleaned.split('```json')[1].split('```')[0]
            elif '```' in cleaned:
                cleaned = cleaned.split('```')[1].split('```')[0]
            
            try:
                data = json.loads(cleaned.strip())
            except Exception as e:
                # Fallback: try ast.literal_eval which is more lenient with single quotes
                try:
                    # Clean the string slightly for literal_eval (remove common AI markers)
                    eval_ready = cleaned.strip()
                    data = ast.literal_eval(eval_ready)
                except:
                    # Last ditch: try to find anything that looks like [ ... ]
                    match = re.search(r'\[.*\]', cleaned, re.DOTALL)
                    if match:
                        try:
                            data = json.loads(match.group(0))
                        except:
                            try:
                                data = ast.literal_eval(match.group(0))
                            except:
                                print(f"FAILED TO PARSE AI OUTPUT:\n{cleaned}\n") # Debug Log
                                raise e
                    else:
                        print(f"NO JSON FOUND IN:\n{cleaned}\n") # Debug Log
                        raise e
        
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
