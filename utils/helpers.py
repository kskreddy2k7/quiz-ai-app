import random
from typing import Dict

QUOTES = [
    {"text": "Education is the most powerful weapon which you can use to change the world.", "author": "Nelson Mandela"},
    {"text": "The beautiful thing about learning is that no one can take it away from you.", "author": "B.B. King"},
    {"text": "Learning is not attained by chance, it must be sought for with ardor.", "author": "Abigail Adams"},
    {"text": "The expert in anything was once a beginner.", "author": "Helen Hayes"},
    {"text": "Success is the sum of small efforts repeated day in and day out.", "author": "Robert Collier"},
    {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"text": "Don't watch the clock; do what it does. Keep going.", "author": "Sam Levenson"},
    {"text": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
    {"text": "Education is not preparation for life; education is life itself.", "author": "John Dewey"}
]

def get_random_quote() -> Dict[str, str]:
    return random.choice(QUOTES)
