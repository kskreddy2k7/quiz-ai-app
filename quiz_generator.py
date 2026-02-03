import requests
import random

HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

HEADERS = {
    "Authorization": "Bearer hf_xxxxxxxxxxxxxxxxx"  
}
# 🔴 Replace with your FREE HuggingFace token

def generate_quiz(text, num_questions=10):
    prompt = f"""
    Generate {num_questions} multiple choice questions for exam preparation.
    Each question should have 4 options and one correct answer.
    Content:
    {text[:1500]}
    """

    response = requests.post(
        HF_API_URL,
        headers=HEADERS,
        json={"inputs": prompt}
    )

    if response.status_code != 200:
        return []

    raw_output = response.json()[0]["generated_text"]

    quiz = []
    blocks = raw_output.split("\n\n")

    for block in blocks:
        lines = block.split("\n")
        if len(lines) >= 6:
            question = lines[0]
            options = lines[1:5]
            answer = lines[5].replace("Answer:", "").strip()

            quiz.append({
                "question": question,
                "options": options,
                "answer": answer
            })

    return quiz
