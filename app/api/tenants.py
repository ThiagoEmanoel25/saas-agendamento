from flask import Blueprint, request, jsonify
from app import db
from app.models import Tenant
import logging
import re

# Configuração de logging
logger = logging.getLogger(__name__)

# Definindo o Blueprint
tenants_bp = Blueprint('tenants', __name__, url_prefix='/tenants')

# Funções auxiliares
def sanitize_subdomain(subdomain):
    """Remove caracteres especiais e normaliza o subdomínio"""
    if not subdomain:
        return ""
    return re.sub(r'[^a-zA-Z0-9-]', '', subdomain).lower()

def validate_tenant_data(data):
    """Valida os dados de entrada para criação de tenant"""
    errors = {}

    if not data:
        return {"error": "Dados não fornecidos"}

    if not data.get('name'):
        errors['name'] = "Nome é obrigatório"

    if not data.get('subdomain'):
        errors['subdomain'] = "Subdomínio é obrigatório"

    return errors if errors else None

def tenant_to_dict(tenant):
    """Converte um objeto Tenant para dicionário"""
    return {
        'id': tenant.id,
        'name': tenant.name,
        'subdomain': tenant.subdomain,
        'is_active': tenant.is_active
    }

# Serviço de Tenant
class TenantService:
    @staticmethod
    def create_tenant(name, subdomain):
        """Cria um novo tenant após validações de negócio"""
        # Sanitiza o subdomínio
        clean_subdomain = sanitize_subdomain(subdomain)

        # Verifica se já existe
        existing_tenant = db.session.execute(
            db.select(Tenant).where(Tenant.subdomain == clean_subdomain)
        ).scalar_one_or_none()

        if existing_tenant:
            raise ValueError("Este subdomínio já está em uso")

        # Cria o tenant sem usar kwargs (evita erro do analisador de tipo)
        new_tenant = Tenant()
        new_tenant.name = name
        new_tenant.subdomain = clean_subdomain

        try:
            db.session.add(new_tenant)
            db.session.commit()
            return new_tenant
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao salvar tenant: {str(e)}", exc_info=True)
            raise RuntimeError(f"Erro ao salvar no banco de dados: {str(e)}")

# Rotas
@tenants_bp.route('/', methods=['POST'])
def create_tenant():
    """Endpoint para criar um novo tenant"""
    try:
        # Obter dados da requisição
        data = request.get_json() or {}

        # Validar dados
        validation_errors = validate_tenant_data(data)
        if validation_errors:
            return jsonify({"error": "Dados inválidos", "details": validation_errors}), 400

        # Criar tenant usando o serviço
        tenant = TenantService.create_tenant(
            name=data['name'],
            subdomain=data['subdomain']
        )

        # Retornar resposta de sucesso
        return jsonify({
            'message': 'Clínica criada com sucesso!',
            'tenant': tenant_to_dict(tenant)
        }), 201

    except ValueError as e:
        # Erro de regra de negócio (ex: subdomínio duplicado)
        return jsonify({'error': str(e)}), 409
    except RuntimeError as e:
        # Erro de banco de dados ou outro erro interno
        return jsonify({'error': "Erro ao processar solicitação", 'details': str(e)}), 500
    except Exception as e:
        # Erro inesperado
        logger.error(f"Erro não tratado ao criar tenant: {str(e)}", exc_info=True)
        return jsonify({'error': "Erro interno do servidor"}), 500