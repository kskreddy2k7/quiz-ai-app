import random
import re

def generate_quiz(text, limit=5):
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if len(s.split()) > 6]

    fallback = ["Python", "Java", "C++", "JavaScript"]
    quiz = []

    for s in sentences[:limit]:
        answer = s.split()[0]
        options = random.sample(fallback, 4)

        if answer not in options:
            options[0] = answer

        random.shuffle(options)

        quiz.append({
            "question": s.replace(answer, "_____"),
            "options": options,
            "answer": answer
        })

    return quiz
