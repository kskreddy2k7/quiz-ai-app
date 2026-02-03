import random

def generate_quiz(text, count, level="easy"):
    keywords = text.split()[:10]

    difficulty_map = {
        "easy": "basic understanding",
        "medium": "concept clarity",
        "hard": "deep application"
    }

    quiz = []
    for i in range(count):
        topic = random.choice(keywords) if keywords else "this topic"
        question = f"What best explains {topic}?"
        options = [
            f"A correct explanation of {topic}",
            f"An unrelated statement",
            f"A common misconception",
            f"An incorrect usage"
        ]

        answer = options[0]

        quiz.append({
            "question": question,
            "options": options,
            "answer": answer,
            "explanation": (
                f"This question checks your {difficulty_map[level]}. "
                f"The correct answer directly explains {topic}."
            )
        })

    return quiz
