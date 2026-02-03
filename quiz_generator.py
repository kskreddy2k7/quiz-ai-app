import random
import re

def generate_quiz(text, count=5):
    sentences = re.split(r'[.?\n]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 40]

    quiz = []
    random.shuffle(sentences)

    for s in sentences[:count]:
        correct = pick_keyword(s)
        options = generate_options(correct)

        quiz.append({
            "question": f"Choose the correct option:\n\n{s}",
            "options": options,
            "answer": correct,
            "explanation": (
                f"The correct answer is '{correct}'.\n\n"
                f"This is because the sentence directly explains the concept "
                f"related to '{correct}'.\n\n"
                f"Other options are incorrect as they do not match the context."
            )
        })

    return quiz


def pick_keyword(sentence):
    words = sentence.split()
    keywords = [w for w in words if len(w) > 5]
    return random.choice(keywords) if keywords else words[0]


def generate_options(correct):
    distractors = [
        "Java", "C++", "Operating System",
        "Database", "Compiler", "Algorithm",
        "Data Structure"
    ]

    options = [correct]
    for d in distractors:
        if d != correct and len(options) < 4:
            options.append(d)

    random.shuffle(options)
    return options
