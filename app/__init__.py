import os
from dotenv import load_dotenv
from flask import Flask
from .database import db
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager  # Importa el JWTManager
from .routes import main

# Inicializa las extensiones
db = SQLAlchemy()
# Inicializa JWTManager
jwt = JWTManager()  
# Cargar las variables de entorno desde el archivo .env
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trivia.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuración de JWT (clave secreta desde variables de entorno)
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)  # Inicializa JWTManager con la aplicación Flask

    # Registrar Blueprints
    from .routes import main  # Asegúrate de importar tu Blueprint

    # Registrar Blueprints
    app.register_blueprint(main)

    return app
