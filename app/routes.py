from flask import Blueprint, request, jsonify
from .crud import create_user, get_users, create_question, get_questions, create_trivia, get_trivias
from app.models import Question, Trivia
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
    return jsonify({"id": question.id, "question_text": question.question_text}), 201

@main.route('/questions', methods=['GET'])
def get_questions_route():
    questions = get_questions()
    return jsonify([{"id": q.id, "question_text": q.question_text} for q in questions])

# Rutas para trivias
@main.route('/trivias', methods=['POST'])
def create_trivia_route():
    data = request.get_json()

    # Validar los datos de entrada
    name = data.get('name')
    description = data.get('description')
    question_ids = data.get('question_ids', [])
    
    if not name or not description:
        return jsonify({"error": "El nombre y la descripción son obligatorios"}), 400
    
    if not question_ids:
        return jsonify({"error": "Se debe proporcionar al menos una pregunta"}), 400

    # Verificar que las preguntas existen
    valid_questions = []
    for question_id in question_ids:
        question = Question.query.get(question_id)
        if question:
            valid_questions.append(question)
        else:
            return jsonify({"error": f"La pregunta con ID {question_id} no existe"}), 400

    # Crear la nueva trivia
    new_trivia = Trivia(name=name, description=description, questions=valid_questions)
    db.session.add(new_trivia)
    db.session.commit()

    return jsonify({"message": "Trivia creada exitosamente", "trivia": {
        "id": new_trivia.id,
        "name": new_trivia.name,
        "description": new_trivia.description,
        "questions": [q.id for q in valid_questions]
    }}), 201

@main.route('/trivias', methods=['GET'])
def get_trivias_route():
    trivias = get_trivias()
    return jsonify([{"id": t.id, "name": t.name} for t in trivias])
