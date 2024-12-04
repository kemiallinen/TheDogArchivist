from flask import Flask
from app.routes import main
from app.database import initialize_database

def create_app():
    app = Flask(__name__)

    initialize_database()

    app.register_blueprint(main)
    return app
