import random
import re

def generate_quiz(text, limit=10):
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if len(s.split()) > 8]

    keywords = list(set(re.findall(r'\b[A-Z][a-z]{3,}\b', text)))
    fallback = ["Python", "Java", "C++", "JavaScript"]

    quiz = []

    for s in sentences[:limit]:
        words = s.split()
        answer = words[0]

        options = random.sample(keywords + fallback, 4)
        if answer not in options:
            options[0] = answer
        random.shuffle(options)

        quiz.append({
            "question": s.replace(answer, "_____"),
            "options": options,
            "answer": answer
        })

    return quiz
