def generate_quiz(text):
    sentences = text.split(".")
    quiz = []

    for sentence in sentences:
        words = sentence.strip().split()

        if len(words) > 6:
            question = f"What is {words[0]}?"
            options = [
                words[1],
                "Option B",
                "Option C",
                "Option D"
            ]

            quiz.append({
                "question": question,
                "options": options,
                "answer": words[1]
            })

        if len(quiz) == 5:
            break

    return quiz
