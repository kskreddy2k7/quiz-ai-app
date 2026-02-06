from __future__ import annotations

import os
import json
import threading
from typing import Callable, List, Dict, Any, Optional

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

import requests
from app.utils.helpers import run_in_thread

class AIService:
    def __init__(self, api_key: Optional[str] = None, backend_url: str = ""):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.backend_url = backend_url
        self.model = None
        self._setup_complete = False
        
        if not self.api_key:
            self._try_load_secrets()

        if self.api_key and HAS_GENAI:
            try:
                genai.configure(api_key=self.api_key)
                
                # Dynamic discovery of models
                available_models = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                # Priority order
                preferred_models = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-pro']
                selected_model_name = None
                
                for pm in preferred_models:
                    if pm in available_models:
                        selected_model_name = pm
                        break
                        
                if not selected_model_name and available_models:
                    selected_model_name = available_models[0]
                    
                if selected_model_name:
                    self.model = genai.GenerativeModel(selected_model_name)
                    self._setup_complete = True
                    print(f"✅ AI Service initialized with model: {selected_model_name}")
                else:
                    print("CRITICAL: No AI models available for this API key.")
            except Exception as e:
                print(f"Direct AI init failed: {e}")

    def is_available(self) -> bool:
        return (self._setup_complete and HAS_GENAI) or bool(self.backend_url)

    def availability_message(self) -> str:
        if self._setup_complete and HAS_GENAI:
            return "AI Online (Direct) 🟢"
        if self.backend_url:
            return "AI Online (Remote) 🟢"
        return "AI Error (Setup Key) 🔴"

    def generate_quiz(
        self,
        topic: str,
        difficulty: str,
        language: str = "English",
        content_text: str = "",
        num_questions: int = 5,
        on_complete: Callable[[List[Dict]], None] = None, 
        on_error: Callable[[str], None] = None
    ) -> None:
        
        # Priority 1: Direct Gemini (Desktop)
        if self._setup_complete and HAS_GENAI:
            self._generate_direct(topic, difficulty, language, content_text, num_questions, on_complete, on_error)
        # Priority 2: Remote Backend (Mobile/Production)
        elif self.backend_url:
            self._generate_remote(topic, difficulty, language, content_text, num_questions, on_complete, on_error)
        else:
            if on_error: on_error("AI Offline: No API Key or Backend URL")

    def _generate_direct(self, topic, diff, lang, context, num, on_complete, on_error):
        prompt = self._build_quiz_prompt(topic, diff, lang, context, num)
        def task():
            response = self.model.generate_content(prompt)
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        run_in_thread(task, on_complete, lambda e: on_error(str(e)))

    def _generate_remote(self, topic, diff, lang, context, num, on_complete, on_error):
        def task():
            # Matches the endpoint in your premium_app.py / web_app.py
            payload = {
                "topic": topic,
                "difficulty": diff,
                "language": lang,
                "num_questions": num,
                "context": context[:2000] # Limiting size for network
            }
            # Try /generate_topic first then fallback to /generate
            resp = requests.post(f"{self.backend_url}/generate_topic", json=payload, timeout=30)
            if resp.status_code != 200:
                resp = requests.post(f"{self.backend_url}/generate", json=payload, timeout=30)
            
            if resp.status_code == 200:
                return resp.json().get("questions", [])
            else:
                raise Exception(f"Server Error: {resp.status_code}")
        
        run_in_thread(task, on_complete, lambda e: on_error(str(e)))

    def _try_load_secrets(self):
        try:
            paths = ["secrets.json", "app/secrets.json", "../secrets.json"]
            for p in paths:
                if os.path.exists(p):
                    with open(p, 'r') as f:
                        data = json.load(f)
                        if "GEMINI_API_KEY" in data:
                            self.api_key = data["GEMINI_API_KEY"]
                            break
        except Exception:
            pass

    def explain_answer(
        self,
        question_text: str,
        correct_answer: str,
        user_answer: str,
        on_complete: Callable[[str], None],
        on_error: Callable[[str], None]
    ) -> None:
        if self._setup_complete and HAS_GENAI:
            prompt = f"Explain why {user_answer} is wrong for question: {question_text}."
            def task():
                resp = self.model.generate_content(prompt)
                return resp.text
            run_in_thread(task, on_complete, lambda e: on_error(str(e)))
        elif self.backend_url:
            def task():
                resp = requests.post(f"{self.backend_url}/ai_help", json={"question": f"Explain mistake: {user_answer} for {question_text}"}, timeout=20)
                return resp.json().get("response", "No explanation available.")
            run_in_thread(task, on_complete, lambda e: on_error(str(e)))

    def solve_doubt(
        self,
        question: str,
        on_complete: Callable[[str], None],
        on_error: Callable[[str], None]
    ) -> None:
        if self._setup_complete and HAS_GENAI:
            def task():
                resp = self.model.generate_content(question)
                return resp.text
            run_in_thread(task, on_complete, lambda e: on_error(str(e)))
        elif self.backend_url:
            def task():
                resp = requests.post(f"{self.backend_url}/ai_help", json={"question": question}, timeout=20)
                return resp.json().get("response", "No help available.")
            run_in_thread(task, on_complete, lambda e: on_error(str(e)))

    def _build_quiz_prompt(self, topic: str, difficulty: str, language: str, context: str, num: int) -> str:
        return f"""
        Generate {num} MCQs on '{topic}' in {language}.
        Difficulty: {difficulty}.
        Output must be a JSON list of objects:
        {{
            "prompt": "Question",
            "choices": ["A", "B", "C", "D"],
            "answer": "Exact text of correct choice",
            "explanation": "Why correct",
            "wrong_explanations": {{"Choice": "Why wrong"}},
            "topic": "{topic}",
            "difficulty": "{difficulty}"
        }}
        """

