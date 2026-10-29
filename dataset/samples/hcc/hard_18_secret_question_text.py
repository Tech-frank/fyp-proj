SECRET_QUESTIONS = [
    "What was the name of your first pet?",
    "In which city were you born?",
]
secret_question_label = "Choose a security question"


def question_choices():
    return list(enumerate(SECRET_QUESTIONS))
