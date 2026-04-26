# app/__init__.py
from flask import Flask
from config import Config
from app.extensions import db, migrate, jwt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    jwt.init_app(app)

    # Importa models
    from app import models

    # Registra Blueprints
    from app.api.tenants import tenants_bp
    app.register_blueprint(tenants_bp)

    from app.api.users import users_bp
    app.register_blueprint(users_bp)

    from app.api.appointments import appointment_bp
    app.register_blueprint(appointment_bp)

    from app.api.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.api.availability import availability_bp
    app.register_blueprint(availability_bp)

    return app