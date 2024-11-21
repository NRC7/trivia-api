import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from .database import db
from flask_jwt_extended import JWTManager
from .routes import main

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos
    # Crear la ruta completa a la base de datos en la raíz del proyecto
    basedir = os.path.abspath(os.path.dirname(__file__))  # Directorio donde está __init__.py
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, '..', 'trivia.db')}"  # Esto crea la base de datos en la raíz del proyecto
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuración de JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    # Inicializar extensiones
    db.init_app(app)
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def expired_token_callback(error, response=None):
        return jsonify({
            "code": "401",
            "message": "La sesión ha caducado, por favor inicia sesión nuevamente."
        }), 401

    # Manejo de error cuando no se proporciona un token o es inválido
    @jwt.unauthorized_loader
    def unauthorized_callback(error, response=None):
        return jsonify({
            "code": "401",
            "message": "No se ha proporcionado un token válido o el token ha expirado."
        }), 401

    # Manejo de error cuando el token es inválido
    @jwt.invalid_token_loader
    def invalid_token_callback(error, response=None):
        return jsonify({
            "code": "401",
            "message": "El token es inválido."
        }), 401

    # Registrar Blueprints
    app.register_blueprint(main)

    return app
