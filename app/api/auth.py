from flask import Blueprint, request, jsonify
from app.extensions import db, jwt
from app.models import User
from flask_jwt_extended import create_access_token

# Define o Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email e senha obrigatorios'}), 400

    # Busca usuário
    user = db.session.execute(
        db.select(User).where(User.email == email)
    ).scalar_one_or_none()

    # Verifica senha
    if not user or not user.check_password(password):
        return jsonify({'error': 'Credenciais invalidas'}), 401

    # Gera token
    access_token = create_access_token(identity=str(user.id))

    return jsonify(access_token=access_token), 200