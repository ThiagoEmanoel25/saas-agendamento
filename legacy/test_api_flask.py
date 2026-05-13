"""
Copiado de test_api.py — testes legados do Flask
"""
import pytest
import json
from app import create_app, db
from app.models import Tenant, User, Appointment
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, time


@pytest.fixture
def app():
    """Criar aplicação de teste"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        
        # Seed básico
        tenant = Tenant(
            name="Test Clinic",
            subdomain="test-clinic",
            is_active=True
        )
        db.session.add(tenant)
        db.session.flush()
        
        doctor = User(
            name="Dr. Test",
            email="doctor@test.com",
            password_hash=generate_password_hash("password123"),
            tenant_id=tenant.id,
            role="doctor"
        )
        
        patient = User(
            name="Patient Test",
            email="patient@test.com",
            password_hash=generate_password_hash("password123"),
            tenant_id=tenant.id,
            role="patient"
        )
        
        db.session.add_all([doctor, patient])
        db.session.commit()
        
        yield app


@pytest.fixture
def client(app):
    """Criar cliente de teste"""
    return app.test_client()


@pytest.fixture
def auth_token(client):
    """Obter token JWT de autenticação"""
    response = client.post('/api/auth/login', 
        json={'email': 'doctor@test.com', 'password': 'password123'},
        content_type='application/json'
    )
    return response.json['access_token']


class TestAuth:
    """Testes de autenticação"""
    
    def test_login_success(self, client):
        """Teste login com sucesso"""
        response = client.post('/api/auth/login',
            json={'email': 'doctor@test.com', 'password': 'password123'},
            content_type='application/json'
        )
        assert response.status_code == 200
        assert 'access_token' in response.json
        assert response.json['user_id'] is not None
    
    def test_login_invalid_password(self, client):
        """Teste login com senha inválida"""
        response = client.post('/api/auth/login',
            json={'email': 'doctor@test.com', 'password': 'wrongpassword'},
            content_type='application/json'
        )
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """Teste login com usuário que não existe"""
        response = client.post('/api/auth/login',
            json={'email': 'nonexistent@test.com', 'password': 'password123'},
            content_type='application/json'
        )
        assert response.status_code == 401
    
    def test_register_success(self, client):
        """Teste registro de novo usuário"""
        response = client.post('/api/auth/register',
            json={
                'email': 'newuser@test.com',
                'name': 'New User',
                'password': 'password123',
                'tenant_id': 1
            },
            content_type='application/json'
        )
        assert response.status_code == 201
        assert 'access_token' in response.json
    
    def test_register_duplicate_email(self, client):
        """Teste registro com email duplicado"""
        response = client.post('/api/auth/register',
            json={
                'email': 'doctor@test.com',
                'name': 'Duplicate User',
                'password': 'password123',
                'tenant_id': 1
            },
            content_type='application/json'
        )
        assert response.status_code == 409


class TestAppointments:
    """Testes de agendamentos"""
    
    def test_list_appointments_without_auth(self, client):
        """Teste listagem sem autenticação"""
        response = client.get('/api/appointments/')
        assert response.status_code == 401
    
    def test_list_appointments_with_auth(self, client, auth_token):
        """Teste listagem com autenticação"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/appointments/',
            headers=headers
        )
        assert response.status_code == 200
        assert 'appointments' in response.json


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])