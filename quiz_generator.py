import random
import re

def generate_quiz(text, limit=5):
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if len(s.split()) > 6]

    fallback = ["Python", "Java", "C++", "JavaScript"]
    quiz = []

    for s in sentences[:limit]:
        words = s.split()
        if not words:
            continue

        answer = words[0]
        options = fallback.copy()

        if answer not in options:
            options[0] = answer

        random.shuffle(options)

        quiz.append({
            "question": s.replace(answer, "_____"),
            "options": options,
            "answer": answer
        })

    return quiz
