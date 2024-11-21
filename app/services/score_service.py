# services/score_service.py

# Diccionario que asigna puntos a cada dificultad
DIFFICULTY_MULTIPLIER = {
    'Fácil': 1,   # 1 punto por cada respuesta correcta en preguntas fáciles
    'Media': 2,   # 2 puntos por cada respuesta correcta en preguntas de dificultad media
    'Difícil': 3  # 3 puntos por cada respuesta correcta en preguntas difíciles
}

def calculate_score(answers, trivia):
    """
    Calcula el puntaje total de un usuario basado en las respuestas correctas
    y la dificultad de las preguntas.
    
    :param answers: Diccionario de respuestas del usuario con {question_id: answer}.
    :param trivia: Objeto Trivia que contiene todas las preguntas.
    :return: El puntaje total del usuario y las respuestas correctas.
    """
    score = 0
    correct_answers = {}

    for question in trivia.questions:
        correct_option = question.correct_option
        user_answer = answers.get(str(question.id))  # Respuesta del usuario para esta pregunta

        # Verifica si la respuesta del usuario es correcta
        if user_answer == correct_option:
            # Asigna puntaje basado en la dificultad de la pregunta
            difficulty_multiplier = DIFFICULTY_MULTIPLIER.get(question.difficulty, 1)
            score += difficulty_multiplier  # Aumenta el puntaje con el multiplicador de dificultad

        correct_answers[question.id] = correct_option  # Guarda la respuesta correcta

    return score, correct_answers
