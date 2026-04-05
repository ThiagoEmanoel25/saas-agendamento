"""
Script para popular o banco de dados com dados de teste
Execute com: python3 seed.py
"""
from app import create_app, db
from app.models import Tenant, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed_database():
    app = create_app()
    
    with app.app_context():
        # Limpar dados existentes
        print("🗑️  Limpando dados antigos...")
        User.query.delete()
        Tenant.query.delete()
        db.session.commit()
        
        # Criar tenant
        print("📦 Criando tenant...")
        tenant = Tenant(
            name="Clínica São João",
            subdomain="clinica-saojoao",
            is_active=True
        )
        db.session.add(tenant)
        db.session.flush()  # Para obter o ID do tenant
        
        # Criar usuários
        print("👥 Criando usuários...")
        
        # Médico
        doctor = User(
            name="Dr. João Silva",
            email="doctor@clinic.com",
            password_hash=generate_password_hash("senha123"),
            tenant_id=tenant.id,
            role="doctor"
        )
        
        # Paciente 1
        patient1 = User(
            name="Maria Santos",
            email="maria@email.com",
            password_hash=generate_password_hash("senha123"),
            tenant_id=tenant.id,
            role="patient"
        )
        
        # Paciente 2
        patient2 = User(
            name="Carlos Oliveira",
            email="carlos@email.com",
            password_hash=generate_password_hash("senha123"),
            tenant_id=tenant.id,
            role="patient"
        )
        
        db.session.add_all([doctor, patient1, patient2])
        db.session.commit()
        
        print("✅ Banco de dados populado com sucesso!")
        print(f"\n📊 Dados criados:")
        print(f"   Tenant: {tenant.name} (ID: {tenant.id})")
        print(f"   Usuários: {len([doctor, patient1, patient2])}")
        print(f"\n🔐 Credenciais de teste:")
        print(f"   Médico:")
        print(f"      Email: doctor@clinic.com")
        print(f"      Senha: senha123")
        print(f"   Paciente 1:")
        print(f"      Email: maria@email.com")
        print(f"      Senha: senha123")
        print(f"   Paciente 2:")
        print(f"      Email: carlos@email.com")
        print(f"      Senha: senha123")


if __name__ == "__main__":
    seed_database()
