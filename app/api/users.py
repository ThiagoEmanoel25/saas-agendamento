from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import User, Tenant
import logging
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
import traceback

logger = logging.getLogger(__name__)

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/', methods=['GET'])
def list_users():
    users = db.session.execute(db.select(User)).scalars().all()
    return jsonify([{"id": u.id, "name": u.name, "email": u.email} for u in users])

@users_bp.route('/debug/', methods=['GET'])
def debug_users():
    """Debug endpoint: mostra estado do banco (tenants, usuários)"""
    try:
        tenants = db.session.execute(db.select(Tenant)).scalars().all()
        users = db.session.execute(db.select(User)).scalars().all()
        return jsonify({
            'tenants': [{'id': t.id, 'name': t.name, 'subdomain': t.subdomain} for t in tenants],
            'users': [{'id': u.id, 'name': u.name, 'email': u.email, 'tenant_id': u.tenant_id} for u in users]
        })
    except Exception as e:
        logger.exception('Erro ao listar debug info')
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@users_bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    # Campos obrigatórios
    if not data.get('name') or not data.get('email') or not data.get('password') or not data.get('tenant_id'):
        return jsonify({'error': 'name, email, password and tenant_id are required'}), 400

    # Garantir que tenant_id seja fornecido e seja inteiro
    tenant_raw = data.get('tenant_id')
    if tenant_raw is None:
        return jsonify({'error': 'tenant_id inválido (não fornecido)'}), 400
    try:
        tenant_id = int(tenant_raw)
    except (ValueError, TypeError):
        return jsonify({'error': 'tenant_id inválido (deve ser numérico)'}), 400

    tenant = db.session.get(Tenant, tenant_id)
    if not tenant:
        return jsonify({'error': 'tenant_id inválido'}), 400

    # Cria usuário e hash da senha
    user = User()
    user.name = data['name']
    user.email = data['email']
    user.password_hash = generate_password_hash(data['password'])
    # Associa ao tenant
    try:
        # Atribui tenant_id diretamente (deve existir no modelo)
        user.tenant_id = tenant_id

        # Log dos valores antes do commit para debugging
        logger.debug('Criando usuário com valores: name=%s, email=%s, tenant_id=%s', user.name, user.email, getattr(user, 'tenant_id', None))

        db.session.add(user)
        db.session.commit()
        return jsonify({'id': user.id, 'name': user.name, 'email': user.email}), 201
    except IntegrityError as ie:
        db.session.rollback()
        logger.exception('IntegrityError ao criar usuário')
        # Tenta extrair a causa da violação de constraint

        ie_str = str(ie.orig) if ie.orig else str(ie)
        return jsonify({'error': 'Dados em conflito ou erro de constraint', 'details': ie_str}), 409
    except Exception as e:
        db.session.rollback()

        # Log completo
        logger.exception('Erro ao criar usuário')


        tb = traceback.format_exc()
        payload = {'error': 'Erro ao criar usuário', 'details': str(e), 'traceback': tb}
        return jsonify(payload), 500
