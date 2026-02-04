from __future__ import annotations

import random
import re
from typing import List, Dict, Any

class MockQuizGenerator:
    """
    Fallback generator that creates questions from text content 
    using keyword extraction/templating when AI is unavailable.
    """

    def generate_quiz(
        self, 
        text: str, 
        num_questions: int = 5, 
        q_type: str = "mixed", 
        topic: str = "General"
    ) -> List[Dict[str, Any]]:
        """
        Generates a list of question dictionaries matching the AI JSON format.
        """
        clean_text = self._clean_text(text)
        sentences = self._split_sentences(clean_text)
        
        # Filter sentences that are too short/long
        candidates = [s for s in sentences if 20 < len(s) < 200]
        
        if not candidates:
            # Fallback if no valid sentences found
            return self._fallback_questions(topic)

        # Shuffle and select
        random.shuffle(candidates)
        selected_sentences = candidates[:num_questions * 2] # Grab extra to ensure we find keywords
        
        questions = []
        for sentence in selected_sentences:
            if len(questions) >= num_questions:
                break
                
            question = self._create_question_from_sentence(sentence, topic)
            if question:
                questions.append(question)
                
        # If we still don't have enough, pad with fallbacks
        while len(questions) < num_questions:
            questions.append(self._generic_question(topic))
            
        return questions

    def _clean_text(self, text: str) -> str:
        # Remove extra whitespace
        return " ".join(text.split())

    def _split_sentences(self, text: str) -> List[str]:
        # Simple split by punctuation
        return re.split(r'(?<=[.!?])\s+', text)

    def _create_question_from_sentence(self, sentence: str, topic: str) -> Optional[Dict[str, Any]]:
        words = sentence.split()
        if len(words) < 5:
            return None
            
        # Try to find a "keyword" (long word, capitalized, etc.)
        # Naive approach: find longest word > 4 chars
        sorted_words = sorted([w for w in words if len(w) > 4], key=len, reverse=True)
        if not sorted_words:
            return None
            
        keyword = sorted_words[0]
        # Clean keyword of punctuation
        keyword_clean = re.sub(r'[^\w\s]', '', keyword)
        
        if len(keyword_clean) < 3:
            return None

        # Create blank
        question_text = sentence.replace(keyword, "_______")
        
        # Distractors (just random logic here since we don't have a dict)
        distractors = self._generate_distractors(keyword_clean)
        
        choices = distractors + [keyword_clean]
        random.shuffle(choices)
        
        return {
            "prompt": f"Complete the sentence:\n\n{question_text}",
            "choices": choices,
            "answer": keyword_clean,
            "explanation": f"The missing word is '{keyword_clean}'. Context: {sentence}",
            "wrong_explanations": {},
            "topic": topic,
            "difficulty": "medium"
        }

    def _generate_distractors(self, correct: str) -> List[str]:
        # Generate simple fake variations
        variations = []
        
        # Variation 1: Reverse
        variations.append(correct[::-1].lower().title())
        
        # Variation 2: Similar length random word or modification
        variations.append(f"Non{correct.lower()}")
        
        # Variation 3: Truncated or extended
        if len(correct) > 5:
            variations.append(correct[:-3])
        else:
            variations.append(correct + "ing")
            
        return variations

    def _fallback_questions(self, topic: str) -> List[Dict[str, Any]]:
        # Same as QuizService demo questions but in dict format
        return [
            {
                "prompt": f"This is a fallback question about {topic}.",
                "choices": ["Correct", "Wrong A", "Wrong B", "Wrong C"],
                "answer": "Correct",
                "explanation": "This is a placeholder generated because no valid text could be parsed.",
                "topic": topic,
                "difficulty": "easy"
            }
        ]

    def _generic_question(self, topic: str) -> Dict[str, Any]:
        return {
            "prompt": "Which of the following is true regarding this topic?",
            "choices": ["It is interesting", "It is boring", "It does not exist", "None of the above"],
            "answer": "It is interesting",
            "explanation": "Learning is always interesting!",
            "topic": topic,
            "difficulty": "easy"
        }
