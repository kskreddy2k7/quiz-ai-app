from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from app.services.ai_service import AIService
from app.services.file_service import FileService
from app.services.quiz_generator import MockQuizGenerator


@dataclass
class QuizQuestion:
    prompt: str
    choices: List[str]
    answer: str
    explanation: str
    wrong_explanations: Dict[str, str] = field(default_factory=dict)
    topic: str = "General"
    difficulty: str = "easy"


class QuizService:
    def __init__(self, ai_service: AIService, local_path: Optional[Path] = None):
        self.ai = ai_service
        self.local_path = local_path
        self.default_difficulty = "easy"
        self.file_service = FileService()
        self.mock_generator = MockQuizGenerator()
        self._init_local_storage()

    def _init_local_storage(self):
        if self.local_path:
            self.local_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.local_path.exists():
                self.local_path.write_text("[]", encoding="utf-8")

    # ---------- OFFLINE ----------
    def load_local_questions(self) -> List[QuizQuestion]:
        if not self.local_path:
            return []
        try:
            data = json.loads(self.local_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = []
        
        if not isinstance(data, list):
            data = []
            
        questions: List[QuizQuestion] = []
        for item in data:
            if isinstance(item, dict) and self._is_valid_question(item):
                questions.append(QuizQuestion(**item))
        return questions

    def save_quiz_offline(self, questions: List[QuizQuestion]) -> None:
        if not self.local_path:
            return
        # Load existing to append or replace? For now, we replace or append?
        # Actually, let's just append new ones to the library
        existing = self.load_local_questions()
        existing_dicts = [q.__dict__ for q in existing]
        
        # Avoid duplicates (simplistic check)
        existing_prompts = {q.prompt for q in existing}
        
        for q in questions:
            if q.prompt not in existing_prompts:
                existing_dicts.append(q.__dict__)
                
        self.local_path.write_text(json.dumps(existing_dicts, indent=2), encoding="utf-8")

    def get_local_quiz(self, subject: str, topic: str, difficulty: str) -> List[QuizQuestion]:
        qs = self.load_local_questions()
        if not qs:
            # Return empty if no local history, rather than demo data
            return []
            
        difficulty = difficulty or self.default_difficulty
        # Filter logic
        matches = [
            q for q in qs 
            if q.difficulty == difficulty 
            and (not topic or q.topic.lower() == topic.lower())
        ]
        
        # Fallback to subject match if topic too specific
        if not matches and subject:
             matches = [q for q in qs if q.topic.lower() == subject.lower()]

        # Fallback to random if still nothing
        if not matches:
            matches = qs

        import random
        random.shuffle(matches)
        return matches[:5]

    # ---------- AI ----------
    def request_ai_quiz(
        self,
        subject: str,
        topic: str,
        difficulty: str,
        language: str = "English",
        content_context: str = "",
        file_path: str = "",
        num_questions: int = 5,
        q_type: str = "mixed",
        on_complete: Callable[[List[QuizQuestion]], None] = None,
        on_error: Callable[[str], None] = None,
    ) -> None:
        
        # 1. Handle File Content
        final_context = content_context
        if file_path:
            try:
                file_text = self.file_service.extract_text(file_path)
                truncated_text = file_text[:12000]
                final_context += f"\n\nSOURCE DOCUMENT:\n{truncated_text}\n"
            except Exception as e:
                if on_error: on_error(f"Docs Error: {e}")
                return

        # 2. Validation
        if (file_path or content_context) and len(final_context.strip()) < 50:
            if on_error: on_error("File/Text content is too short or empty.")
            return
            
        # 3. Call AI Service
        def success(data: List[Dict]) -> None:
            try:
                questions: List[QuizQuestion] = []
                for item in data:
                    item["topic"] = topic or subject
                    item["difficulty"] = difficulty
                    
                    # Ensure choices is list
                    if "choices" in item and isinstance(item["choices"], str):
                         # sometimes AI acts up and gives a string
                         try: item["choices"] = json.loads(item["choices"])
                         except: pass
                         
                    if self._is_valid_question(item):
                        # Filter out extra keys that match QuizQuestion fields but might be wrong type
                        valid_keys = QuizQuestion.__dataclass_fields__.keys()
                        filtered_item = {k: v for k, v in item.items() if k in valid_keys}
                        # Add missing defaults if needed? Dataclass handles it mostly
                        questions.append(QuizQuestion(**filtered_item))
                
                if not questions:
                    fail("No valid questions generated from AI.")
                    return

                self.save_quiz_offline(questions)
                if on_complete:
                    on_complete(questions)
            except Exception as e:
                fail(f"Parsing Logic Error: {e}")

        def fail(msg: str) -> None:
            print(f"DEBUG: Quiz Gen Failed -> {msg}")
            if on_error: on_error(msg)
        
        # Determine strict topic or general subject
        target_topic = topic if topic else subject
        
        self.ai.generate_quiz(
            topic=target_topic,
            difficulty=difficulty,
            language=language,
            content_text=final_context,
            num_questions=num_questions,
            on_complete=success,
            on_error=fail
        )

    def _parse_ai_response(
        self, text: str, topic: str, difficulty: str
    ) -> List[QuizQuestion]:
        raw = text.strip()
        # Clean markdown code blocks
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("Failed to parse AI quiz format") from exc
            
        if not isinstance(data, list):
            raise ValueError("AI response was not a list")
            
        questions: List[QuizQuestion] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            
            # Normalize fields
            item["topic"] = topic
            item["difficulty"] = difficulty
            
            if self._is_valid_question(item):
                questions.append(QuizQuestion(**item))
                
        if not questions:
            raise ValueError("No valid questions parsed from AI response")
            
        return questions

    def _is_valid_question(self, item: dict) -> bool:
        required = {"prompt", "choices", "answer", "explanation"}
        if not required.issubset(item.keys()):
            return False
            
        # Basic validation
        if not isinstance(item["choices"], list) or len(item["choices"]) < 2:
            return False
        if item["answer"] not in item["choices"]:
            return False
            
        return True

    def _demo_questions(self) -> List[QuizQuestion]:
        # Return a small set of hardcoded demo questions
        return [
            QuizQuestion(
                topic="General",
                difficulty="easy",
                prompt="What is the powerhouse of the cell?",
                choices=["Mitochondria", "Nucleus", "Ribosome", "Golgi body"],
                answer="Mitochondria",
                explanation="Mitochondria are known as the powerhouse of the cell because they generate most of the cell's supply of adenosine triphosphate (ATP).",
                wrong_explanations={
                    "Nucleus": "The nucleus controls the cell's activities.",
                    "Ribosome": "Ribosomes make proteins.",
                    "Golgi body": "The Golgi body packages proteins."
                }
            )
        ]
