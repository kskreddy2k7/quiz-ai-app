import random

def generate_quiz(text, count, level="easy"):
    words = [w for w in text.split() if len(w) > 4]
    if not words:
        words = ["learning", "concept", "knowledge"]

    difficulty_hint = {
        "easy": "basic understanding",
        "medium": "concept clarity",
        "hard": "deep application"
    }

    quiz = []

    for _ in range(count):
        keyword = random.choice(words)

        question = f"What best explains **{keyword}**?"

        options = [
            f"A clear and correct explanation of {keyword}",
            f"An unrelated idea",
            f"A common misunderstanding",
            f"An incorrect usage"
        ]

        random.shuffle(options)

        answer = next(o for o in options if "correct explanation" in o)

        explanation = (
            f"This question checks your {difficulty_hint[level]}. "
            f"The correct answer directly explains what {keyword} means in context."
        )

        quiz.append({
            "question": question,
            "options": options,
            "answer": answer,
            "explanation": explanation
        })

    return quiz
