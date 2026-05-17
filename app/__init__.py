from flask import Flask
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()

login_manager = LoginManager()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')

    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    jwt.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    return app
