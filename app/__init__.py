# app/__init__.py
from flask import Flask
from config import Config
from app.extensions import db, Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate.init_app(app, db)

    # Importa models
    from app import models

    # Registra Blueprints
    from app.api.tenants import tenants_bp
    app.register_blueprint(tenants_bp)

    from app.api.users import users_bp
    app.register_blueprint(users_bp)

    from app.api.appointments import appointment_bp
    app.register_blueprint(appointment_bp)

    return app