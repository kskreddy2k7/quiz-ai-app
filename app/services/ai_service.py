from __future__ import annotations

import requests
import json
from typing import Callable, List, Dict, Any
from app.utils.helpers import run_in_thread

class AIService:
    """
    Client-side service that communicates with the Backend API.
    Does NOT hold API keys. Does NOT import google.generativeai.
    """
    def __init__(self, backend_url: str = "http://127.0.0.1:8000"):
        self.backend_url = backend_url.rstrip("/")

    def is_available(self) -> bool:
        """Check if backend is reachable"""
        try:
            resp = requests.get(f"{self.backend_url}/health", timeout=5)
            return resp.status_code == 200
        except:
            return False

    def availability_message(self) -> str:
        if self.is_available():
            return "Server: Online 🟢"
        return "Server: Offline 🔴 (Check Connection)"

    def _handle_request_error(self, e: Exception) -> str:
        """Maps technical errors to user-friendly messages."""
        if isinstance(e, requests.exceptions.Timeout):
            return "Network is slow. Please check your internet and try again."
        
        if isinstance(e, requests.exceptions.ConnectionError):
            return "Unable to connect to server. Please try later."

        if isinstance(e, requests.exceptions.HTTPError):
            code = e.response.status_code
            if code == 429:
                return "AI usage limit reached. Please try again later."
            if code >= 500:
                return "Our servers are busy. Please try again in a moment."
            # Extract detail if possible
            try:
                return e.response.json().get("detail", "Unexpected response. Please retry.")
            except:
                pass
        
        return "Unexpected error. Please check your connection."

    def generate_quiz(
        self,
        topic: str,
        difficulty: str,
        content_text: str,
        on_complete: Callable[[List[Dict]], None],
        on_error: Callable[[str], None]
    ) -> None:
        
        def task() -> List[Dict]:
            payload = {
                "topic": topic,
                "difficulty": difficulty,
                "content_text": content_text
            }
            try:
                resp = requests.post(f"{self.backend_url}/generate-quiz", json=payload, timeout=45)
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.RequestException as e:
                raise Exception(self._handle_request_error(e))
            except Exception as e:
                # Json parse error etc
                raise Exception("Invalid response from server. Please retry.")

        run_in_thread(
            task,
            on_complete,
            lambda err_msg: on_error(str(err_msg))
        )
        
    def explain_answer(
        self,
        question_text: str,
        correct_answer: str,
        user_answer: str,
        on_complete: Callable[[str], None],
        on_error: Callable[[str], None]
    ) -> None:
        
        def task() -> str:
            payload = {
                "question_text": question_text,
                "correct_answer": correct_answer,
                "user_answer": user_answer
            }
            try:
                resp = requests.post(f"{self.backend_url}/explain-answer", json=payload, timeout=20)
                resp.raise_for_status()
                return resp.json().get("explanation", "")
            except requests.exceptions.RequestException as e:
                raise Exception(self._handle_request_error(e))

        run_in_thread(
            task,
            on_complete,
            lambda err_msg: on_error(str(err_msg))
        )

    def solve_doubt(
        self,
        question: str,
        on_complete: Callable[[str], None],
        on_error: Callable[[str], None]
    ) -> None:
        
        def task() -> str:
            payload = {"question": question}
            try:
                resp = requests.post(f"{self.backend_url}/ask-doubt", json=payload, timeout=20)
                resp.raise_for_status()
                return resp.json().get("answer", "")
            except requests.exceptions.RequestException as e:
                raise Exception(self._handle_request_error(e))

        run_in_thread(
            task,
            on_complete,
            lambda err_msg: on_error(str(err_msg))
        )

