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

        question = f"🤖 AI Quick-Check: What best explains **{key}**?"

        correct = f"{key} is explained clearly with correct meaning"
        wrong1 = f"{key} is misunderstood here"
        wrong2 = f"{key} is used incorrectly"
        wrong3 = f"{key} has no relation to this topic"

        options = [correct, wrong1, wrong2, wrong3]
        random.shuffle(options)

        explanation = (
            f"📘 This question checks your {depth[level]}.\n"
            f"✅ The correct answer explains {key} accurately."
        )

        option_explanations = {
            correct: f"✅ Correct: {key} is described with the right meaning and context.",
            wrong1: f"❌ Not quite: this option shows a common misunderstanding about {key}.",
            wrong2: f"❌ Not quite: {key} is applied in the wrong way here.",
            wrong3: f"❌ Not quite: this option ignores the topic and doesn't relate to {key}."
        }

        quiz.append({
            "question": question,
            "options": options,
            "answer": correct,
            "explanation": explanation,
            "option_explanations": option_explanations
        })

    return quiz
