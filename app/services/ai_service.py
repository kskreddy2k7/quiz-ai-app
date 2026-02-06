from __future__ import annotations

import os
import google.generativeai as genai
from typing import Callable
from app.utils.helpers import run_in_thread

class AIService:
    """
    Central service for interacting with Google Gemini AI.
    Handles API keys, client initialization, and error formatting.
    """
    def __init__(self, model_name: str = "gemini-pro"):
        self.model_name = model_name
        self.model = None
        self.api_key = None
        self._refresh_client()

    def _refresh_client(self) -> None:
        # Load API key from env
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)

    def set_api_key(self, key: str) -> None:
        """Allow setting API key at runtime"""
        os.environ["GEMINI_API_KEY"] = key
        self._refresh_client()

    def is_available(self) -> bool:
        self._refresh_client()
        return bool(self.api_key)

    def availability_message(self) -> str:
        self._refresh_client()
        if not self.api_key:
            return "AI Mode: Offline 📴 (Missing Gemini Key)"
        return "AI Mode: Online ✨ (Gemini Active)"

    def _friendly_error(self, exc: Exception | None = None) -> str:
        if not self.api_key:
            return "📴 AI is offline. Please enter your Gemini API key."
        
        message = str(exc).lower() if exc else ""
        if "connection" in message or "timeout" in message:
            return "📴 Check your internet connection."
        if "quota" in message or "429" in message:
            return "⚠️ AI quota exceeded. Try again later."
            
        print(f"DEBUG: Gemini Error: {exc}") 
        return "🤖 AI service unavailable."

    def run_async(
        self,
        prompt: str,
        system_prompt: str,
        on_complete: Callable[[str], None],
        on_error: Callable[[str], None],
        temperature: float = 0.7
    ) -> None:
        self._refresh_client()

        def task() -> str:
            if not self.api_key or not self.model:
                raise RuntimeError("No Gemini API key provided")

            # Gemini doesn't use system prompts the same way as GPT, 
            # but we can prepend it or use the safety settings/config.
            # For simplicity, we prepend context.
            full_prompt = f"{system_prompt}\n\nUser: {prompt}"
            
            try:
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature
                    )
                )
                if response.parts:
                    return response.text.strip()
                return ""
            except Exception as e:
                raise e

        run_in_thread(
            task,
            on_complete,
            lambda message: on_error(self._friendly_error(Exception(message))),
        )
