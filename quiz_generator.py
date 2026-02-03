import random
import re

def extract_keywords(text):
    words = re.findall(r"[A-Za-z]{5,}", text)
    keywords = list(set(words))
    return keywords[:20] if keywords else ["learning", "concept", "knowledge"]

def generate_quiz(text, count, level="easy"):
    keywords = extract_keywords(text)

    depth = {
        "easy": "basic understanding",
        "medium": "concept clarity",
        "hard": "real application"
    }

    quiz = []

    for i in range(count):
        key = random.choice(keywords)

        question = f"🤔 What best explains **{key}**?"

        correct = f"{key} is explained clearly with correct meaning"
        wrong1 = f"{key} is misunderstood here"
        wrong2 = f"{key} is used incorrectly"
        wrong3 = f"{key} has no relation to this topic"

        options = [correct, wrong1, wrong2, wrong3]
        random.shuffle(options)

        explanation = (
            f"📘 This question checks your {depth[level]}.\n"
            f"✅ The correct answer explains {key} accurately, "
            f"while others are misconceptions students usually make."
        )

        quiz.append({
            "question": question,
            "options": options,
            "answer": correct,
            "explanation": explanation
        })

    return quiz
