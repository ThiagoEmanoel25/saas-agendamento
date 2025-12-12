from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def login():
    data = request.get_json() or {}

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email e Senha são obrigatórios"}), 400

    user = db.session.execute(
        db.select(User).where(User.email == email)
    ).scalar_one_or_none()

    # Verifica se o usuário existe e a senha está correta
    if not user or not user.check_password(password):
        return jsonify({"error": "Credenciais inválidas"}), 401

    # Cria o token de acesso JWT
    access_token = create_access_token(identity=str(user.id), additional_claims={"tenant_id": user.tenant_id})

    return jsonify({
        'message': "Login realizado com sucesso!",
        'access_token': access_token,
        'user': {'id': user.id, 'name': user.name, 'email': user.email,}
    }), 200