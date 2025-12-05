from flask import Flask
from flask_migrate import Migrate
from config import Config
from app import db

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Importa os modelos
    from app import models

    # Registra os blueprints
    from app.api.tenants import tenants_bp
    app.register_blueprint(tenants_bp)
    # Registrar blueprint de usuários (se existir)
    try:
        from app.api.users import users_bp
        app.register_blueprint(users_bp)
    except Exception:
        # Se o módulo não existir ou falhar na importação, não interrompe a criação da app
        pass
    return app