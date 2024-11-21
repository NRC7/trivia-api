from flask import Blueprint, request, jsonify
from .crud import create_user, get_users, create_question, get_questions, create_trivia, get_trivias
from app.models import Question, Trivia, Participate, Ranking, User
from app.database import db
from sqlalchemy.exc import IntegrityError


# Crear el Blueprint
main = Blueprint('main', __name__)

# Ruta de prueba
@main.route('/welcome')
def index():
    return "¡Bienvenido a la API de Trivia!"

# Rutas para usuarios
@main.route('/users', methods=['POST'])
def create_user_route():

    data = request.get_json()

    try:
        # Intentar crear un nuevo usuario
        user = create_user(data['name'], data['email'])
        return jsonify({
            "code": "201",
            "message": "Usuario creado exitosamente",
            "data": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }), 201

    except IntegrityError as e:
        # Si hay un error de integridad (como clave duplicada)
        return jsonify({
            "code": "400",
            "message": "El usuario ya existe"
        }), 400

    except Exception as e:
        # Manejo de otros errores internos
        return jsonify({
            "code": "500",
            "message": "Faltan datos necesarios"
        }), 500

@main.route('/users', methods=['GET'])
def get_users_route():
    # Obtener la lista de usuarios
    users = get_users()

    # Validación: Si no hay usuarios, devolver 404
    if not users:
        return jsonify({
            "code": "404",
            "message": "No se encontraron usuarios"
        }), 404

    return jsonify({
        "code": "200",
        "message": "Usuarios recuperados exitosamente",
        "data": [
            {"id": user.id, "name": user.name, "email": user.email} for user in users
        ]
    }), 200

# Rutas para preguntas
@main.route('/questions', methods=['POST'])
def create_question_route():

    data = request.get_json()

    # Validación de campos
    if not all(key in data for key in ['question_text', 'correct_option', 'options', 'difficulty']):
        return jsonify({
            "code": "400",
            "message": "Faltan datos necesarios"
        }), 400

    try:
        question = create_question(
            data['question_text'], 
            data['correct_option'], 
            data['options'], 
            data['difficulty']
        )

        return jsonify({
            "code": "201",
            "message": "Pregunta creada exitosamente",
            "data": {
                "id": question.id,
                "question_text": question.question_text,
                "difficulty": question.difficulty
            }
        }), 201

    except IntegrityError as e:
        return jsonify({
            "code": "400",
            "message": "La pregunta ya existe o hay un error en los datos proporcionados."
        }), 400

    except Exception as e:
        return jsonify({
            "code": "500",
            "message": "Faltan datos necesarios"
        }), 500

@main.route('/questions', methods=['GET'])
def get_questions_route():
    questions = get_questions()

    if not questions:
        return jsonify({
            "code": "404",
            "message": "No se encontraron preguntas.",
        }), 404

    response_data = [
        {
            "id": q.id,
            "question_text": q.question_text,
            "options": {
                "option_1": q.option_1,
                "option_2": q.option_2,
                "option_3": q.option_3
            },
            "correct_option": q.correct_option,
            "difficulty": q.difficulty
        }
        for q in questions
    ]

    return jsonify({
        "code": "200",
        "length": len(response_data),
        "message": "Preguntas recuperadas exitosamente",
        "data": response_data
    }), 200


# Rutas para trivias
@main.route('/trivias', methods=['POST'])
def create_trivia_route():
    data = request.get_json()

    # Verificar que 'name' y 'description' estén presentes en los datos
    name = data.get('name')
    description = data.get('description', '')  # Si no se manda descripción, será un string vacío
    user_ids = data.get('user_ids', [])

    # Validar que se haya proporcionado un nombre
    if not name:
        return jsonify({
            "code": "400",
            "message": "Debes ingresar nombre",  
            "error": "BAD_REQUEST"
        }), 400

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
            return jsonify({
                "code": "400",
                "message": f"La pregunta con ID {question_id} no existe",
                "error": "BAD_REQUEST"
            }), 400

    # Asociar las preguntas válidas con la trivia
    new_trivia.questions = valid_questions

    # Obtener los usuarios de la base de datos mediante los IDs proporcionados
    valid_users = []
    for user_id in user_ids:
        user = User.query.get(user_id)
        if user:
            valid_users.append(user)
        else:
            return jsonify({
                "code": "400",
                "message": f"El usuario con ID {user_id} no existe",
                "error": "BAD_REQUEST"
            }), 400

    # Asociar los usuarios válidos con la trivia
    new_trivia.users = valid_users

    # Guardar en la base de datos
    db.session.add(new_trivia)
    db.session.commit()

    return jsonify({
        "code": "201",
        "message": "Trivia creada exitosamente",
        "data": {
            "id": new_trivia.id,
            "name": new_trivia.name,
            "description": new_trivia.description,
            "questions": [q.id for q in valid_questions],
            "users": [{"id": user.id, "name": user.name} for user in valid_users]
        }
    }), 201



@main.route('/trivias', methods=['GET'])
def get_all_trivias():
    # Obtener todas las trivias de la base de datos
    trivias = Trivia.query.all()

    # Si no se encuentran trivias, devolver un error 404
    if not trivias:
        return jsonify({"code": "404", "message": "No se han encontrado trivias", "data": []}), 404

    # Crear una lista de las trivias con su nombre, descripción y preguntas
    trivias_data = []
    for trivia in trivias:
        trivia_data = {
            "id": trivia.id,
            "name": trivia.name,
            "description": trivia.description,
            "questions": [{"id": q.id, "question_text": q.question_text} for q in trivia.questions],
            "users": [{"id": user.id, "name": user.name} for user in trivia.users]
        }
        trivias_data.append(trivia_data)

    return jsonify({
        "code": "200",
        "length": len(trivias_data),
        "message": "Trivias obtenidas exitosamente",
        "data": trivias_data
    }), 200


# Ruta para participar en una trivia
@main.route('/participate', methods=['POST'])
def participate():
    data = request.get_json()

    user_id = data.get('user_id') 
    trivia_id = data.get('trivia_id')
    answers = data.get('answers')  # Ejemplo: { "1": "option_1", "2": "option_3" }

    # Validar que los datos estén presentes
    if not user_id or not trivia_id or not answers:
        return jsonify({
            "code": "400",
            "message": "Faltan datos necesarios"
        }), 400

    # Verificar que la trivia existe
    trivia = Trivia.query.get(trivia_id)
    if not trivia:
        return jsonify({
            "code": "404",
            "message": "Trivia no encontrada"
        }), 404
    
    # Verificar que el usuario existe
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "code": "404",
            "message": "Usuario no encontrado"
        }), 404

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

        is_correct = option_value == correct_option
        
        # Validar si la respuesta del usuario es correcta
        if is_correct:
            # Obtener la dificultad de la pregunta (como número)
            difficulty = question.difficulty  # Asegúrate de que 'difficulty' sea un número entero

            # Ajustar el puntaje según la dificultad
            if difficulty == "fácil":  
                score += 1  
            elif difficulty == "medio": 
                score += 2  
            elif difficulty == "difícil":  
                score += 3  
            else:
                print(f"Dificultad desconocida para la pregunta {question.id}: {difficulty}")  # Si la dificultad es desconocida 
        
        # Guardar la respuesta correcta para la pregunta
        correct_answers[question.id] = {
            "correct_answer": correct_option,
            "difficulty": question.difficulty,
            "is_correct": "correcta" if is_correct else "incorrecta"
        }

    # Guardar participación
    participation = Participate(user_id=user_id, trivia_id=trivia_id, answers=answers, score=score)
    db.session.add(participation)
    db.session.commit()

    # Guardar en el ranking
    ranking = Ranking(trivia_id=trivia_id, user_id=user_id, score=score)
    db.session.add(ranking)
    db.session.commit()

    # Responder con el puntaje y las respuestas correctas
    return jsonify({
        "code": "201",
        "message": "Participación registrada",
        "data": {
            "score": score,
            "correct_answers": correct_answers,  # Incluyendo las respuestas correctas
            "trivia": {
                "id": trivia.id,
                "name": trivia.name
            }
        }
    }), 201



# Ruta para obtener el ranking de una trivia
@main.route('/ranking/<int:trivia_id>', methods=['GET'])
def ranking(trivia_id):
    # Obtener la trivia por ID
    trivia = Trivia.query.get(trivia_id)
    if not trivia:
        return jsonify({
            "code": "400",
            "message": "Trivia no encontrada",
            "error": "BAD_REQUEST"
        }), 400

    # Obtener los rankings ordenados por puntaje de mayor a menor
    rankings = Ranking.query.filter_by(trivia_id=trivia_id).order_by(Ranking.score.desc()).all()

    if not rankings:
        return jsonify({
            "code": "400",
            "message": "No hay participantes para esta trivia",
            "error": "BAD_REQUEST"
        }), 400

    # Construir la lista de rankings
    ranking_list = [
        {
            "user_id": ranking.user_id,
            "user_name": ranking.user.name,
            "score": ranking.score
        }
        for ranking in rankings
    ]

    # Retornar la respuesta con el nombre de la trivia
    return jsonify({
        "code": "200",
        "message": "Ranking recuperado exitosamente",
        "data": {
            "trivia": {
                "id": trivia.id,
                "name": trivia.name,
                "descripcion": trivia.description
            },
            "ranking": ranking_list
        }
    }), 200

# Ruta para obtener las trivias de un usuario en especifico
@main.route('/users/<int:user_id>/trivias', methods=['GET'])
def get_user_trivias(user_id):
    # Buscar el usuario por ID
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            "code": "404",
            "message": "Usuario no encontrado"
        }), 404

    # Obtener las trivias asociadas a este usuario
    trivias = user.trivias  # Esto es posible gracias a la relación definida en el modelo User
    
    # Si no tiene trivias asignadas
    if not trivias:
        return jsonify({
            "code": "404",
            "message": "Este usuario no tiene trivias asignadas"
        }), 404

    # Formatear las trivias para la respuesta
    trivias_data = []
    for trivia in trivias:
        trivia_data = {
            "id": trivia.id,
            "name": trivia.name,
            "description": trivia.description,
            "questions": [{"id": q.id, "question_text": q.question_text} for q in trivia.questions]
        }
        trivias_data.append(trivia_data)

    # Devolver la lista de trivias asignadas
    return jsonify({
        "code": "200",
        "message": f"Trivias de {user.name} obtenidas exitosamente",
        "data": trivias_data,
        "len": len(trivias_data),
        "user": {
            "id": user.id,
            "user_name": user.name
            }
    }), 200
