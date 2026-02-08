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
        
        # Connection pooling for better performance
        self._session = None
        self._client_timeout = aiohttp.ClientTimeout(total=60, connect=10)
        
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

    async def _get_session(self):
        """Get or create a persistent session for connection pooling."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._client_timeout)
        return self._session
    
    async def close(self):
        """Close the session when shutting down."""
        if self._session and not self._session.closed:
            await self._session.close()

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
        
        session = await self._get_session()
        async with session.post(url, headers=headers, json=payload) as response:
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
        """Generate quiz with optimized retry logic and faster failure detection."""
        last_error = None
        max_attempts = 2  # Reduced from 3 for faster failure feedback
        
        for attempt in range(max_attempts):
            try:
                text = await self.generate_text(prompt)
                return self._parse_json(text)
            except Exception as e:
                print(f"Quiz generation attempt {attempt+1} failed: {e}")
                last_error = e
                # Shorter wait between retries for faster user feedback
                if attempt < max_attempts - 1:
                    await asyncio.sleep(0.5)
        
        raise last_error or Exception(f"Failed to generate quiz after {max_attempts} attempts")

    async def chat_with_teacher(self, history: List[Dict[str, str]], message: str, user_context: Optional[Dict] = None) -> str:
        """Chat with the Friendly Teacher persona with personalization."""
        system_prompt = (
            "You are a friendly, encouraging, and patient teacher. "
            "Your goal is to help students understand concepts deeply. "
            "Use simple language, analogies, and ASCII charts/diagrams where helpful. "
            "Never give just the answer; explain the 'why'. "
            "Keep responses concise but helpful."
        )
        
        # Add personalization if user context is provided
        if user_context:
            # Sanitize user name to prevent prompt injection
            name = user_context.get('name', 'Student')
            # Remove any newlines, special characters that could inject prompts
            name = ''.join(c for c in name if c.isalnum() or c.isspace())[:50]
            level = user_context.get('level', 1)
            
            system_prompt += f"\n\nYou are currently helping {name} (Level {level}). "
            if level >= 5:
                system_prompt += "They are an advanced learner, so feel free to use more sophisticated language and dive deeper into topics."
            elif level >= 3:
                system_prompt += "They are making good progress. Encourage them and provide intermediate-level explanations."
            else:
                system_prompt += "They are just starting their learning journey. Use very simple language and lots of encouragement."
        
        # Construct full prompt
        full_prompt = f"System: {system_prompt}\n\n"
        for msg in history:
            # Ensure role is mapped correctly
            role = "Teacher" if msg['role'] == "model" or msg['role'] == "assistant" else "Student"
            full_prompt += f"{role}: {msg['content']}\n"
        full_prompt += f"Student: {message}\nTeacher:"
        
        return await self.generate_text(full_prompt)

    async def explain_concept(self, text: str, context: Optional[str] = None) -> str:
        """Provide a deep, step-by-step explanation with research-grade quality."""
        prompt = (
            f"Act as a premium Academic AI Tutor. Explain the following concept deeply:\n"
            f"Topic: '{text}'\n\n"
            "## Strict Output Rules:\n"
            "1. **Summary**: Start with a precise 1-2 line summary.\n"
            "2. **Core Logic**: Explain 'WHY' this works and 'HOW' it functions (not just 'WHAT').\n"
            "3. **Structure**: Use clear headings and bullet points.\n"
            "4. **Analogy**: Use a relatable real-world analogy.\n"
            "5. **Visual**: Include a small ASCII diagram/chart to visualize the concept.\n"
            "6. **References**: List 2-3 standard textbooks or credible fields of study for further reading.\n"
        )
        if context:
            prompt += f"\nContext from file/quiz: {context}\n"
            
        return await self.generate_text(prompt)

    async def summarize_text(self, text: str) -> str:
        """Generate a concise summary of the text."""
        prompt = (
            f"Summarize the following text in 3-4 bullet points, capturing the key concepts:\n"
            f"'{text[:10000]}'\n" # Limit input to avoid overload
            f"\nSummary:"
        )
        return await self.generate_text(prompt)

    async def generate_presentation_content(self, topic: str, num_slides: int, language: str, theme: str = "Modern", tone: str = "Professional") -> Dict[str, Any]:
        """Generate professional presentation content with a specific persona."""
        
        system_prompt = (
            "You are a professional AI presentation designer and educator, similar to Canva's AI. "
            "Your job is to CREATE, STYLE, and PREVIEW presentations automatically. "
            "Work at production level quality.\n\n"
            f"Topic: {topic}\n"
            f"Target Audience/Tone: {tone}\n"
            f"Language: {language}\n"
            f"Slide Count: {num_slides} (Target 8-12 for full depth)\n\n"
            "## Strict Design Rules:\n"
            "1. **Flow**: Title -> Intro -> Core Concepts (3-4 slides) -> Real-world Examples -> Summary/Conclusion.\n"
            "2. **Content**: Max 5 bullet points per slide. No walls of text. concise & punchy.\n"
            "3. **Visuals**: Every slide MUST have a `visual_cue` field describing a relevant image.\n"
            "4. **Layout**: Use variety (`title_bullets`, `two_column`, `quote_center`, `image_right`, `section_header`).\n\n"
            "## JSON Structure:\n"
            "{\n"
            "  \"title\": \"Presentation Title\",\n"
            "  \"theme\": \"Requested Theme\",\n"
            "  \"font\": \"Recommended Font\",\n"
            "  \"slides\": [\n"
            "    {\n"
            "      \"layout\": \"image_right\",\n"
            "      \"title\": \"Slide Title\",\n"
            "      \"content\": [\"Point 1\", \"Point 2\", \"Point 3\"],\n"
            "      \"visual_cue\": \"Wide shot of a Mars colony with domes\"\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        
        try:
            text = await self.generate_text(system_prompt)
            data = self._parse_json(text)
            
            # Validation
            if not isinstance(data, dict) or "slides" not in data:
                raise ValueError("Invalid AI response structure")
                
            return data
            
        except Exception as e:
            print(f"Presentation Gen Error: {e}")
            # Fallback
            return {
                "title": topic,
                "theme": theme,
                "slides": [
                    {"title": "Introduction", "content": ["Overview of " + topic]},
                    {"title": "Key Concepts", "content": ["Concept 1", "Concept 2"]},
                    {"title": "Conclusion", "content": ["Summary", "Thank you"]}
                ]
            }

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
        # Standardize format
        if isinstance(data, dict):
            # Quiz Format
            for key in ['questions', 'quiz', 'items']:
                if key in data and isinstance(data[key], list):
                    return data[key]
            # Presentation Format
            if 'slides' in data:
                return data
            # Single Question
            if 'prompt' in data and 'choices' in data:
                return [data]
            # Generic Dict (let caller validate)
            return data
        
        if isinstance(data, list):
            return data
            
        raise ValueError("AI returned invalid JSON structure")

ai_service = AIService()
