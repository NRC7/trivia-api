from .database import db

# Tabla de asociación para la relación muchos a muchos entre Trivia y Question
trivia_questions = db.Table(
    'trivia_questions',
    db.Column('trivia_id', db.Integer, db.ForeignKey('trivia.id'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id'), primary_key=True)
)

class Trivia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    questions = db.relationship('Question', secondary=trivia_questions, back_populates='trivias')

    def __repr__(self):
        return f'<Trivia {self.name}>'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(100), nullable=False)
    option_1 = db.Column(db.String(100), nullable=False)
    option_2 = db.Column(db.String(100), nullable=False)
    option_3 = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    trivias = db.relationship('Trivia', secondary=trivia_questions, back_populates='questions')

    def __repr__(self):
        return f'<Question {self.question_text}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'
