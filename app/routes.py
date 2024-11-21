from flask import Blueprint, request, jsonify
from .crud import create_user, get_users, create_question, get_questions, create_trivia, get_trivias
from app.models import Question, Trivia, Participate, Ranking
from app.database import db


# Crear el Blueprint
main = Blueprint('main', __name__)

# Ruta de prueba
@main.route('/')
def index():
    return "¡Bienvenido a la API de Trivia!"

# Rutas para usuarios
@main.route('/users', methods=['POST'])
def create_user_route():
    data = request.get_json()
    user = create_user(data['name'], data['email'])
    return jsonify({"id": user.id, "name": user.name, "email": user.email}), 201

@main.route('/users', methods=['GET'])
def get_users_route():
    users = get_users()
    return jsonify([{"id": user.id, "name": user.name, "email": user.email} for user in users])

# Rutas para preguntas
@main.route('/questions', methods=['POST'])
def create_question_route():
    data = request.get_json()
    question = create_question(data['question_text'], data['correct_option'], data['options'], data['difficulty'])
    return jsonify({"id": question.id, "question_text": question.question_text, "difficulty": question.difficulty}), 201

@main.route('/questions', methods=['GET'])
def get_questions_route():
    questions = get_questions()

    # Construir la respuesta con la pregunta y las opciones
    response = [
        {
            "id": q.id,
            "question_text": q.question_text,
            "options": {
                "option_1": q.option_1,
                "option_2": q.option_2,
                "option_3": q.option_3
            },
            "correct_option": q.correct_option,  # Incluyendo la respuesta correcta,
            "difficulty": q.difficulty # Añadir la dificultad en la respuesta
        }
        for q in questions
    ]

    return jsonify(response)


# Rutas para trivias
@main.route('/trivias', methods=['POST'])
def create_trivia_route():
    data = request.get_json()

    # Verificar que 'name' y 'description' estén presentes en los datos
    name = data.get('name')
    description = data.get('description', '')  # Si no se manda descripción, será un string vacío

    # Validar que se haya proporcionado un nombre
    if not name:
        return jsonify({"error": "El nombre es obligatorio"}), 400

    # Crear la nueva trivia
    new_trivia = Trivia(name=name, description=description)

    # Obtener las preguntas de la base de datos mediante los IDs proporcionados
    question_ids = data.get('question_ids', [])
    valid_questions = []
    for question_id in question_ids:
        question = Question.query.get(question_id)
        if question:
            valid_questions.append(question)
        else:
            return jsonify({"error": f"La pregunta con ID {question_id} no existe"}), 400

    # Asociar las preguntas válidas con la trivia
    new_trivia.questions = valid_questions

    # Guardar en la base de datos
    db.session.add(new_trivia)
    db.session.commit()

    return jsonify({
        "message": "Trivia creada exitosamente",
        "trivia": {
            "id": new_trivia.id,
            "name": new_trivia.name,
            "description": new_trivia.description,
            "questions": [q.id for q in valid_questions]
        }
    }), 201



@main.route('/trivias', methods=['GET'])
def get_all_trivias():
    # Obtener todas las trivias de la base de datos
    trivias = Trivia.query.all()

    # Si no se encuentran trivias, devolver un error 404
    if not trivias:
        return jsonify({"error": "No se han encontrado trivias"}), 404

    # Crear una lista de las trivias con su nombre, descripción y preguntas
    trivias_data = []
    for trivia in trivias:
        trivia_data = {
            "id": trivia.id,
            "name": trivia.name,
            "description": trivia.description,
            "questions": [{"id": q.id, "question_text": q.question_text} for q in trivia.questions]
        }
        trivias_data.append(trivia_data)

    return jsonify({"trivias": trivias_data}), 200


# Ruta para participar en una trivia
@main.route('/participate', methods=['POST'])
def participate():
    data = request.get_json()

    user_name = data.get('user_name')
    trivia_id = data.get('trivia_id')
    answers = data.get('answers')  # Ejemplo: { "1": "option_1", "2": "option_3" }

    # Verificar que la trivia existe
    trivia = Trivia.query.get(trivia_id)
    if not trivia:
        return jsonify({"error": "Trivia no encontrada"}), 404

    # Validar respuestas y calcular el puntaje
    score = 0
    correct_answers = {}  # Para devolver las respuestas correctas

    for question in trivia.questions:
        correct_option = question.correct_option  # La respuesta correcta, por ejemplo 'París'
        user_answer = answers.get(str(question.id))  # Respuesta del usuario, como 'option_1'

        # Acceder a las opciones de la pregunta (deberías tener 'option_1', 'option_2', 'option_3' en tu modelo)
        options = {
            "option_1": question.option_1,
            "option_2": question.option_2,
            "option_3": question.option_3
        }

        # Obtener el valor de la opción seleccionada por el usuario
        option_value = options.get(user_answer)

        # Validar si la respuesta del usuario es correcta
        if option_value == correct_option:
            # Obtener la dificultad de la pregunta (como número)
            difficulty = question.difficulty  # Asegúrate de que 'difficulty' sea un número entero

            # Ajustar el puntaje según la dificultad
            if difficulty == 1:  # Dificultad fácil
                score += 1  # 1 punto por respuesta correcta
            elif difficulty == 2:  # Dificultad media
                score += 2  # 2 puntos por respuesta correcta
            elif difficulty == 3:  # Dificultad difícil
                score += 3  # 3 puntos por respuesta correcta
            else:
                print(f"Dificultad desconocida para la pregunta {question.id}: {difficulty}")  # Si la dificultad es desconocida 
        
        # Guardar la respuesta correcta para la pregunta
        correct_answers[question.id] = correct_option

    # Guardar participación
    participation = Participate(user_name=user_name, trivia_id=trivia_id, answers=answers, score=score)
    db.session.add(participation)
    db.session.commit()

    # Guardar en el ranking
    ranking = Ranking(trivia_id=trivia_id, user_name=user_name, score=score)
    db.session.add(ranking)
    db.session.commit()

    # Responder con el puntaje y las respuestas correctas
    return jsonify({
        "message": "Participación registrada",
        "score": score,
        "correct_answers": correct_answers  # Incluyendo las respuestas correctas
    }), 201



# Ruta para obtener el ranking de una trivia
@main.route('/ranking/<int:trivia_id>', methods=['GET'])
def ranking(trivia_id):
    # Obtener la trivia por ID
    trivia = Trivia.query.get(trivia_id)
    if not trivia:
        return jsonify({"error": "Trivia no encontrada"}), 404

    # Obtener los rankings ordenados por puntaje de mayor a menor
    rankings = Ranking.query.filter_by(trivia_id=trivia_id).order_by(Ranking.score.desc()).all()

    if not rankings:
        return jsonify({"error": "No hay participantes para esta trivia"}), 404

    # Construir la lista de rankings
    ranking_list = [{"user_name": ranking.user_name, "score": ranking.score} for ranking in rankings]

    # Retornar la respuesta con el nombre de la trivia
    return jsonify({
        "trivia": {
            "id": trivia.id,
            "name": trivia.name
        },
        "ranking": ranking_list
    }), 200
