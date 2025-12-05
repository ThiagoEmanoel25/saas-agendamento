from flask_sqlalchemy import SQLAlchemy

# Cria a instância do banco de dados
db = SQLAlchemy()

def init_app(app):
    """Inicializa o banco de dados com a aplicação Flask"""
    db.init_app(app)


def create_app(*args, **kwargs):
    """Wrapper para expor a factory `create_app` do pacote `app.api`.

    Importa internamente para evitar import circular entre `app` e `app.api`.
    """
    from .api import create_app as _create_app
    return _create_app(*args, **kwargs)
