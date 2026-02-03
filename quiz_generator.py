import json
import os
import random
import re
import urllib.request
from urllib.error import URLError, HTTPError

def extract_keywords(text):
    words = re.findall(r"[A-Za-z]{5,}", text)
    keywords = list(set(words))
    return keywords[:20] if keywords else ["learning", "concept", "knowledge"]

def _build_local_quiz(text, count, level):
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


def _request_ai_quiz(text, count, level):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    system_prompt = (
        "You are an AI quiz generator. Respond with strict JSON only. "
        "Generate multiple-choice questions with 4 options each, include the correct answer, "
        "a short overall explanation, and per-option explanations."
    )
    user_prompt = (
        f"Topic or source text:\n{text}\n\n"
        f"Difficulty: {level}\n"
        f"Number of questions: {count}\n\n"
        "Return JSON in this shape:\n"
        "{\n"
        '  "questions": [\n'
        "    {\n"
        '      "question": "string",\n'
        '      "options": ["A", "B", "C", "D"],\n'
        '      "answer": "exactly one of the options",\n'
        '      "explanation": "short explanation",\n'
        '      "option_explanations": {\n'
        '        "A": "why A is correct/incorrect",\n'
        '        "B": "why B is correct/incorrect",\n'
        '        "C": "why C is correct/incorrect",\n'
        '        "D": "why D is correct/incorrect"\n'
        "      }\n"
        "    }\n"
        "  ]\n"
        "}\n"
    )

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }).encode("utf-8")

    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return None

    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return None

    questions = parsed.get("questions")
    if not isinstance(questions, list) or not questions:
        return None

    normalized = []
    for item in questions[:count]:
        question = item.get("question")
        options = item.get("options")
        answer = item.get("answer")
        explanation = item.get("explanation", "")
        option_explanations = item.get("option_explanations", {})
        if (
            not isinstance(question, str)
            or not isinstance(options, list)
            or len(options) != 4
            or answer not in options
        ):
            continue
        if not isinstance(option_explanations, dict):
            option_explanations = {}
        normalized.append({
            "question": f"🤖 AI Quick-Check: {question}",
            "options": options,
            "answer": answer,
            "explanation": explanation,
            "option_explanations": option_explanations
        })

    return normalized if normalized else None


def generate_quiz(text, count, level="easy"):
    ai_quiz = _request_ai_quiz(text, count, level)
    if ai_quiz:
        return ai_quiz, "ai"

    return _build_local_quiz(text, count, level), "local"
