from flask import Flask
from .database import db
from .routes import main

def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trivia.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensiones
    db.init_app(app)

    # Registrar Blueprints
    app.register_blueprint(main)

    return app
