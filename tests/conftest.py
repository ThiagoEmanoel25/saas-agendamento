import os
import pytest

# Garantir que a configuração de DB de teste exista antes de importar create_app
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('JWT_SECRET_KEY', 'test-jwt-key')

from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope='session')
def app():
    """Cria a aplicação Flask em modo de teste."""
    app = create_app()
    app.config['TESTING'] = True
    # Garantir que use sqlite em memória durante os testes
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    return app


@pytest.fixture(scope='session')
def db(app):
    """Cria o schema no início da sessão e remove ao final."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    """Cliente de teste para fazer requisições à app."""
    return app.test_client()
