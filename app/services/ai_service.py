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

from app.utils.helpers import run_in_thread

class AIService:
    """
    Direct client for Google Gemini API.
    Removes the need for a separate backend server.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = None
        self._setup_complete = False
        
        # Try to load from local secrets if not invalid
        if not self.api_key:
            self._try_load_secrets()

        if self.api_key and HAS_GENAI:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self._setup_complete = True
            except Exception as e:
                print(f"AI Service configuration error: {e}")

    def _try_load_secrets(self):
        try:
            # Look in various locations
            paths = ["secrets.json", "app/secrets.json", "../secrets.json"]
            for p in paths:
                if os.path.exists(p):
                    with open(p, 'r') as f:
                        data = json.load(f)
                        if "GEMINI_API_KEY" in data:
                            self.api_key = data["GEMINI_API_KEY"]
                            print(f"Loaded API Key from {p}")
                            break
        except Exception as e:
            print(f"Failed to load secrets: {e}")

    def is_available(self) -> bool:
        return self._setup_complete and HAS_GENAI

    def availability_message(self) -> str:
        if not HAS_GENAI:
            return "Missing Library (pip install google-generativeai)"
        if not self.api_key:
            return "Missing API Key"
        if self._setup_complete:
            return "AI Online 🟢"
        return "AI Error 🔴"

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
        
        if not self.is_available():
            if on_error: on_error("AI Service Unavailable")
            return

        prompt = self._build_quiz_prompt(topic, difficulty, language, content_text, num_questions)

        def task():
            try:
                response = self.model.generate_content(prompt)
                text = response.text
                # Cleanup typical markdown json blocks
                text = text.replace("```json", "").replace("```", "").strip()
                data = json.loads(text)
                return data
            except Exception as e:
                raise Exception(f"AI Generation Failed: {str(e)}")

        run_in_thread(task, on_complete, lambda e: on_error(str(e)))

    def _build_quiz_prompt(self, topic: str, difficulty: str, language: str, context: str, num: int) -> str:
        # Heavily engineered prompt for the requirement
        base = f"""
        Act as an expert tutor for Indian students.
        Generate {num} multiple-choice questions (MCQs) on the topic: '{topic}'.
        Difficulty Level: {difficulty}.
        Language: {language} (If not English, provide the question in {language} but keep technical terms clear).

        CRITICAL: The output must be a valid JSON list of objects.
        
        Required JSON Structure for each question:
        {{
            "prompt": "The question text here",
            "choices": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "The exact text of the correct option",
            "explanation": "A simple student-friendly explanation of why the answer is correct.",
            "wrong_explanations": {{
                "Option A": "Specific reason why this option is wrong (keep it simple)",
                "Option B": "Specific reason why this option is wrong",
                ... (for all wrong options)
            }},
            "topic": "{topic}",
            "difficulty": "{difficulty}"
        }}

        Constraints:
        1. "wrong_explanations" keys must match the incorrect options exactly.
        2. Explanations should be encouraging and educational ("Why this answer is wrong").
        3. No simple "It is wrong" answers. Explain the CONCEPT error.
        """
        
        if context:
            base += f"\n\nContext Material to use for questions:\n{context[:5000]}"
            
        return base

    def explain_answer(
        self,
        question_text: str,
        correct_answer: str,
        user_answer: str,
        on_complete: Callable[[str], None],
        on_error: Callable[[str], None]
    ) -> None:
        # If we have pre-generated explanations, we might not strictly need this,
        # but for dynamic chat or deeper explanation:
        prompt = f"""
        Student answered: "{user_answer}"
        Correct answer: "{correct_answer}"
        Question: "{question_text}"
        
        Explain why their answer is wrong (if it is) and why the correct one is right.
        Keep it short (max 2 sentences) and friendly.
        """
        
        def task():
            if not self.is_available(): return "Offline mode explanation."
            resp = self.model.generate_content(prompt)
            return resp.text

        run_in_thread(task, on_complete, lambda e: on_error(str(e)))

    def solve_doubt(
        self,
        question: str,
        on_complete: Callable[[str], None],
        on_error: Callable[[str], None]
    ) -> None:
        
        def task():
            if not self.is_available(): return "AI is offline."
            resp = self.model.generate_content(f"You are a helpful tutor. Student asks: {question}\nAnswer briefly and clearly.")
            return resp.text

        run_in_thread(task, on_complete, lambda e: on_error(str(e)))
