import requests

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

def generate_quiz(text, num_questions=10):
    prompt = f"""
Generate {num_questions} exam-style multiple choice questions.
Each question must have 4 options and one correct answer.

Content:
{text[:1200]}
"""

    response = requests.post(
        API_URL,
        json={"inputs": prompt},
        timeout=60
    )

    if response.status_code != 200:
        print("HF Error:", response.text)
        return []

    data = response.json()

    if not isinstance(data, list):
        return []

    output = data[0].get("generated_text", "")

    quiz = []
    lines = output.split("\n")

    for i in range(0, len(lines)-5, 6):
        quiz.append({
            "question": lines[i],
            "options": lines[i+1:i+5],
            "answer": lines[i+1]  # safe fallback
        })

        if len(quiz) == num_questions:
            break

    return quiz
