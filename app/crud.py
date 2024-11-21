from .models import User, Question, Trivia
from .database import db

def register_user(name, email, hashed_password, role="jugador"):
    """Registra un usuario con contraseña hasheada y rol."""
    user = User(name=name, email=email, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()
    return user

def get_user_by_email(email):
    """Busca un usuario por email."""
    return User.query.filter_by(email=email).first()

# Crear un usuario
def create_user(name, email):
    user = User(name=name, email=email)
    db.session.add(user)
    db.session.commit()
    return user

# Obtener todos los usuarios
def get_users():
    return User.query.all()

# Crear una pregunta
def create_question(question_text, correct_option, options, difficulty):
    question = Question(
        question_text=question_text,
        correct_option=correct_option,
        option_1=options[0],
        option_2=options[1],
        option_3=options[2],
        difficulty=difficulty
    )
    db.session.add(question)
    db.session.commit()
    return question

# Obtener todas las preguntas
def get_questions():
    return Question.query.all()

# Crear una trivia
def create_trivia(name, description, question_ids):
    trivia = Trivia(name=name, description=description)
    for question_id in question_ids:
        question = Question.query.get(question_id)
        trivia.questions.append(question)
    db.session.add(trivia)
    db.session.commit()
    return trivia

# Obtener todas las trivias
def get_trivias():
    return Trivia.query.all()
