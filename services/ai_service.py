import os
import json
import asyncio
import aiohttp
import google.generativeai as genai
import ast
import re
import hashlib
import sqlite3
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class AIService:
    # Configuration constants
    MAX_CACHE_ENTRIES = 1000
    MAX_CACHED_PROMPT_LENGTH = 1000
    PROVIDER_TIMEOUT = 10  # seconds
    CONNECTION_TIMEOUT = 5  # seconds
    FAILURE_THRESHOLD = 3
    COOLDOWN_DURATION = 30  # seconds
    MAX_TOKEN_LENGTH = 2048
    MAX_CHAT_HISTORY = 8  # messages
    MAX_FILE_CONTENT = 15000  # characters
    
    def __init__(self):
        self.cloudflare_api_key = os.getenv("CLOUDFLARE_API_KEY", "")
        self.cloudflare_account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        
        self.has_ai = False
        self.provider = "None"
        self.status = "Offline"
        self.model = None
        self.fallback_models = []
        self.current_provider = None
        
        # Connection pooling for better performance
        self._session = None
        self._client_timeout = aiohttp.ClientTimeout(
            total=self.PROVIDER_TIMEOUT, 
            connect=self.CONNECTION_TIMEOUT
        )
        
        # Response cache
        self._cache_db = "ai_cache.db"
        self._init_cache()
        
        # Provider health tracking
        self._provider_failures = {}
        self._provider_cooldown = {}
        
        self._initialize_providers()

    def _init_cache(self):
        """Initialize SQLite cache for AI responses."""
        try:
            conn = sqlite3.connect(self._cache_db)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_cache (
                    prompt_hash TEXT PRIMARY KEY,
                    prompt TEXT,
                    response TEXT,
                    provider TEXT,
                    created_at TIMESTAMP,
                    access_count INTEGER DEFAULT 1
                )
            ''')
            # Create index for faster lookups (hybrid frequency/recency for cache eviction)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_count ON ai_cache(access_count DESC, created_at DESC)')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Cache init error: {e}")
    
    def _initialize_providers(self):
        # Refresh from environment
        self.cloudflare_api_key = os.getenv("CLOUDFLARE_API_KEY", "").split('#')[0].strip().strip('"')
        self.cloudflare_account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").split('#')[0].strip().strip('"')
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "").split('#')[0].strip().strip('"')
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY", "").split('#')[0].strip().strip('"')

        # Initialize Gemini if key exists
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                # Try primary model first, with fallback options
                self.fallback_models = [
                    'models/gemini-1.5-flash-latest',
                    'models/gemini-1.5-pro-latest',
                    'gemini-1.5-flash-latest',
                    'gemini-1.5-pro-latest'
                ]
                
                # Use the first model without testing during init to avoid slow startup
                # Model validation will happen on first actual use
                model_name = self.fallback_models[0]
                self.model = genai.GenerativeModel(model_name)
                self.has_ai = True
                self.provider = "Gemini"
                self.status = "Online (Gemini)"
                self.current_provider = "gemini"

                self.provider = f"Gemini ({model_name})"
                self.status = f"Online (Gemini {model_name})"
                print(f"Initialized Gemini with model: {model_name}")

            except Exception as e:
                print(f"Gemini init error: {e}")

        if self.cloudflare_api_key and self.cloudflare_account_id:
            self.has_ai = True
            if not self.gemini_api_key:
                self.provider = "Cloudflare"
                self.status = "Online (Cloudflare)"
                self.current_provider = "cloudflare"
        
        if self.huggingface_api_key:
            self.has_ai = True
            if not self.gemini_api_key and not (self.cloudflare_api_key and self.cloudflare_account_id):
                self.provider = "HuggingFace"
                self.status = "Online (HuggingFace)"
                self.current_provider = "huggingface"
        
        # Always mark as having AI available (we have offline fallbacks)
        if not self.has_ai:
            self.has_ai = True  # Always available with offline mode
            self.provider = "Offline"
            self.status = "Offline Mode (Rule-based)"
            self.current_provider = "offline"

    async def _get_session(self):
        """Get or create a persistent session for connection pooling."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._client_timeout)
        return self._session
    
    async def close(self):
        """Close the session when shutting down."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key from prompt."""
        # Compress prompt by removing extra whitespace
        compressed = ' '.join(prompt.split())
        return hashlib.md5(compressed.encode()).hexdigest()
    
    def _get_from_cache(self, prompt: str) -> Optional[str]:
        """Retrieve response from cache if available."""
        try:
            cache_key = self._get_cache_key(prompt)
            conn = sqlite3.connect(self._cache_db)
            cursor = conn.cursor()
            
            # Get cached response
            cursor.execute(
                'SELECT response, provider FROM ai_cache WHERE prompt_hash = ?',
                (cache_key,)
            )
            result = cursor.fetchone()
            
            if result:
                # Update access count
                cursor.execute(
                    'UPDATE ai_cache SET access_count = access_count + 1 WHERE prompt_hash = ?',
                    (cache_key,)
                )
                conn.commit()
                conn.close()
                print(f"✓ Cache hit for prompt (provider: {result[1]})")
                return result[0]
            
            conn.close()
            return None
        except Exception as e:
            print(f"Cache read error: {e}")
            return None
    
    def _save_to_cache(self, prompt: str, response: str, provider: str):
        """Save response to cache."""
        try:
            cache_key = self._get_cache_key(prompt)
            conn = sqlite3.connect(self._cache_db)
            cursor = conn.cursor()
            
            # Limit prompt size in cache
            prompt_truncated = prompt[:self.MAX_CACHED_PROMPT_LENGTH] if len(prompt) > self.MAX_CACHED_PROMPT_LENGTH else prompt
            
            cursor.execute('''
                INSERT OR REPLACE INTO ai_cache 
                (prompt_hash, prompt, response, provider, created_at, access_count)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (cache_key, prompt_truncated, response, provider, datetime.now()))
            
            conn.commit()
            conn.close()
            
            # Clean old cache entries (keep last 1000)
            self._cleanup_cache()
        except Exception as e:
            print(f"Cache write error: {e}")
    
    def _cleanup_cache(self):
        """Remove old cache entries using hybrid frequency/recency eviction strategy."""
        try:
            conn = sqlite3.connect(self._cache_db)
            cursor = conn.cursor()
            
            # Keep the MAX_CACHE_ENTRIES most frequently/recently accessed entries
            # Prioritizes frequently used entries (access_count), with recency as tiebreaker
            cursor.execute(f'''
                DELETE FROM ai_cache WHERE prompt_hash NOT IN (
                    SELECT prompt_hash FROM ai_cache 
                    ORDER BY access_count DESC, created_at DESC 
                    LIMIT {self.MAX_CACHE_ENTRIES}
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Cache cleanup error: {e}")
    
    def _is_provider_on_cooldown(self, provider: str) -> bool:
        """Check if provider is on cooldown after failures."""
        if provider not in self._provider_cooldown:
            return False
        
        cooldown_until = self._provider_cooldown[provider]
        if time.time() < cooldown_until:
            return True
        
        # Cooldown expired, reset
        del self._provider_cooldown[provider]
        self._provider_failures[provider] = 0
        return False
    
    def _mark_provider_failure(self, provider: str):
        """Track provider failures and set cooldown if needed."""
        self._provider_failures[provider] = self._provider_failures.get(provider, 0) + 1
        
        # After FAILURE_THRESHOLD failures, put on COOLDOWN_DURATION cooldown
        if self._provider_failures[provider] >= self.FAILURE_THRESHOLD:
            self._provider_cooldown[provider] = time.time() + self.COOLDOWN_DURATION
            print(f"⚠️ {provider} on cooldown for {self.COOLDOWN_DURATION}s after {self._provider_failures[provider]} failures")
    
    def _mark_provider_success(self, provider: str):
        """Reset failure count on successful call."""
        if provider in self._provider_failures:
            self._provider_failures[provider] = 0

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
        
        # Try with the current model first
        loop = asyncio.get_event_loop()
        
        # If current model fails, try fallback models
        for model_name in self.fallback_models:
            try:
                # Update model if needed
                if self.provider != f"Gemini ({model_name})":
                    current_model = genai.GenerativeModel(model_name)
                    self.provider = f"Gemini ({model_name})"
                    print(f"Trying Gemini model: {model_name}")
                else:
                    current_model = self.model
                
                # Use local variable to avoid closure issues
                response = await loop.run_in_executor(None, lambda m=current_model: m.generate_content(prompt))
                
                # Success - update the instance model
                self.model = current_model
                return response.text
            except Exception as e:
                print(f"Gemini model {model_name} failed: {e}")
                # Continue to next model
                continue
        
        # If all models failed
        raise Exception("All Gemini models failed. Please try again later.")
        response = await loop.run_in_executor(None, lambda: self.model.generate_content(prompt))
        return response.text
    
    async def generate_with_huggingface(self, prompt: str, model: str = "mistralai/Mistral-7B-Instruct-v0.2") -> str:
        """Generate text using Hugging Face Inference API (free tier)."""
        url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}",
            "Content-Type": "application/json"
        }
        
        # Different models have different input formats
        if "mistral" in model.lower() or "llama" in model.lower():
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": self.MAX_TOKEN_LENGTH,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "return_full_text": False
                }
            }
        else:
            # For simpler models like T5
            payload = {
                "inputs": prompt,
                "parameters": {"max_length": self.MAX_TOKEN_LENGTH}
            }
        
        session = await self._get_session()
        try:
            async with session.post(url, headers=headers, json=payload, timeout=self._client_timeout) as response:
                if response.status == 200:
                    result = await response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get('generated_text', str(result[0]))
                    elif isinstance(result, dict):
                        return result.get('generated_text', str(result))
                    return str(result)
                elif response.status == 503:
                    # Model is loading, might work on retry
                    raise Exception("HuggingFace model loading, try again")
                else:
                    text = await response.text()
                    raise Exception(f"HuggingFace API error: {response.status} - {text}")
        except asyncio.TimeoutError:
            raise Exception("HuggingFace timeout")
    
    def generate_offline_quiz(self, topic: str, num_questions: int, difficulty: str) -> List[Dict[str, Any]]:
        """Generate a basic quiz using rule-based logic when all AI providers fail."""
        # Template-based quiz generation
        questions = []
        
        # Generic quiz templates
        templates = [
            {
                "prompt": f"What is the primary purpose of {topic}?",
                "choices": [
                    f"To solve complex problems related to {topic}",
                    f"To demonstrate basic principles of {topic}",
                    f"To provide entertainment only",
                    f"None of the above"
                ],
                "answer": f"To solve complex problems related to {topic}",
                "explanation": f"The primary purpose of {topic} is to address and solve problems in its domain."
            },
            {
                "prompt": f"Which of the following is a key concept in {topic}?",
                "choices": [
                    f"Fundamental principles of {topic}",
                    "Random unrelated concepts",
                    "Entertainment value",
                    "None apply"
                ],
                "answer": f"Fundamental principles of {topic}",
                "explanation": f"Understanding fundamental principles is crucial for mastering {topic}."
            },
            {
                "prompt": f"What is an important application of {topic}?",
                "choices": [
                    f"Real-world problem solving in {topic}",
                    "Creating confusion",
                    "Making things complicated",
                    "No applications exist"
                ],
                "answer": f"Real-world problem solving in {topic}",
                "explanation": f"{topic} has practical applications in solving real-world problems."
            }
        ]
        
        # Generate requested number of questions
        for i in range(min(num_questions, len(templates))):
            questions.append(templates[i])
        
        # If more questions needed, cycle through templates with variations
        while len(questions) < num_questions:
            base = templates[len(questions) % len(templates)].copy()
            base["prompt"] = f"Question {len(questions) + 1}: {base['prompt']}"
            questions.append(base)
        
        return questions[:num_questions]

    async def generate_quiz(self, prompt: str) -> List[Dict[str, Any]]:
        """Generate quiz with multi-provider fallback and caching."""
        # Try to get from cache first
        cached = self._get_from_cache(prompt)
        if cached:
            try:
                return self._parse_json(cached)
            except Exception as e:
                print(f"Cache parse error: {e}")
        
        # Try all providers in order
        last_error = None
        used_provider = None
        
        try:
            text = await self.generate_text(prompt)
            parsed = self._parse_json(text)
            # Cache successful response
            self._save_to_cache(prompt, json.dumps(parsed), self.current_provider)
            return parsed
        except Exception as e:
            print(f"AI generation failed, using offline fallback: {e}")
            last_error = e
        
        # Ultimate fallback: offline quiz generation
        # Extract topic and number from prompt
        topic_match = re.search(r'about "([^"]+)"', prompt)
        topic = topic_match.group(1) if topic_match else "general knowledge"
        
        num_match = re.search(r'Generate (\d+)', prompt)
        num_questions = int(num_match.group(1)) if num_match else 5
        
        diff_match = re.search(r'Difficulty: (\w+)', prompt)
        difficulty = diff_match.group(1) if diff_match else "medium"
        
        print(f"⚡ Using offline quiz generator for: {topic}")
        offline_quiz = self.generate_offline_quiz(topic, num_questions, difficulty)
        
        # Cache offline response too
        self._save_to_cache(prompt, json.dumps(offline_quiz), "offline")
        
        return offline_quiz

    async def chat_with_teacher(self, history: List[Dict[str, str]], message: str, user_context: Optional[Dict] = None) -> str:
        """Chat with the Friendly Teacher persona with personalization and caching."""
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
        
        # Limit history to last MAX_CHAT_HISTORY messages for efficiency
        recent_history = history[-self.MAX_CHAT_HISTORY:] if len(history) > self.MAX_CHAT_HISTORY else history
        
        # Construct full prompt
        full_prompt = f"System: {system_prompt}\n\n"
        for msg in recent_history:
            # Ensure role is mapped correctly
            role = "Teacher" if msg['role'] == "model" or msg['role'] == "assistant" else "Student"
            full_prompt += f"{role}: {msg['content']}\n"
        full_prompt += f"Student: {message}\nTeacher:"
        
        try:
            return await self.generate_text(full_prompt)
        except Exception as e:
            # Fallback response
            return ("I'm experiencing some technical difficulties, but I'm here to help! "
                   "Could you rephrase your question? Meanwhile, try breaking down the problem into smaller parts.")

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
        
        try:
            return await self.generate_text(prompt)
        except Exception as e:
            # Fallback explanation
            return (f"**{text}**\n\n"
                   f"This is a concept that requires understanding of fundamental principles. "
                   f"To learn more about {text}, I recommend:\n"
                   f"1. Breaking it down into smaller components\n"
                   f"2. Looking for real-world examples\n"
                   f"3. Practicing with simple exercises\n\n"
                   f"*Note: Using offline mode - for detailed explanations, please try again when online.*")

    async def summarize_text(self, text: str) -> str:
        """Generate a concise summary of the text."""
        prompt = (
            f"Summarize the following text in 3-4 bullet points, capturing the key concepts:\n"
            f"'{text[:10000]}'\n" # Limit input to avoid overload
            f"\nSummary:"
        )
        try:
            return await self.generate_text(prompt)
        except Exception as e:
            # Fallback summary
            words = text.split()
            return (f"**Summary (Offline Mode)**\n\n"
                   f"• Document contains approximately {len(words)} words\n"
                   f"• Key topics may include: {', '.join(words[:5])}\n"
                   f"• For detailed summary, please try again when online\n")

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
        """Generic text generation with multi-provider fallback and caching."""
        # Check cache first
        cached = self._get_from_cache(prompt)
        if cached:
            return cached
        
        # Compress prompt to save tokens
        compressed_prompt = ' '.join(prompt.split())
        
        # Try providers in priority order with timeout and cooldown checks
        providers = []
        
        # Build provider list based on availability and cooldown status
        if self.gemini_api_key and not self._is_provider_on_cooldown("gemini"):
            providers.append(("gemini", self.generate_with_gemini))
        
        if self.cloudflare_api_key and self.cloudflare_account_id and not self._is_provider_on_cooldown("cloudflare"):
            providers.append(("cloudflare", self.generate_with_cloudflare))
        
        if self.huggingface_api_key and not self._is_provider_on_cooldown("huggingface"):
            providers.append(("huggingface", self.generate_with_huggingface))
        
        # Try each provider
        for provider_name, provider_func in providers:
            try:
                print(f"🤖 Trying {provider_name}...")
                
                # Set timeout for each provider
                response = await asyncio.wait_for(
                    provider_func(compressed_prompt),
                    timeout=self.PROVIDER_TIMEOUT
                )
                
                # Success!
                self.current_provider = provider_name
                self._mark_provider_success(provider_name)
                self._save_to_cache(prompt, response, provider_name)
                print(f"✓ {provider_name} succeeded")
                return response
                
            except asyncio.TimeoutError:
                print(f"⏱️ {provider_name} timeout")
                self._mark_provider_failure(provider_name)
                continue
            except Exception as e:
                print(f"❌ {provider_name} failed: {str(e)[:100]}")
                self._mark_provider_failure(provider_name)
                continue
        
        # All providers failed, check cache for any similar past responses
        # (This is a last resort - return a generic error message)
        raise Exception("⚡ All AI providers temporarily unavailable. Using offline mode.")

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
