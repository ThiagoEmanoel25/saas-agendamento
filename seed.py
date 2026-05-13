"""Seed script updated to use FastAPI SQLAlchemy SessionLocal.
Run with: python3 seed.py
"""
from fastapi_app.db import SessionLocal
from fastapi_app import models
from werkzeug.security import generate_password_hash


def seed_database():
    db = SessionLocal()
    try:
        print("🗑️  Limpando dados antigos...")
        db.query(models.User).delete()
        db.query(models.Tenant).delete()
        db.commit()

        print("📦 Criando tenant...")
        tenant = models.Tenant(name="Clínica São João", subdomain="clinica-saojoao", is_active=True)
        db.add(tenant)
        db.flush()

        print("👥 Criando usuários...")
        doctor = models.User(
            name="Dr. João Silva",
            email="doctor@clinic.com",
            password_hash=generate_password_hash("senha123"),
            tenant_id=tenant.id,
            role="doctor"
        )

        patient1 = models.User(
            name="Maria Santos",
            email="maria@email.com",
            password_hash=generate_password_hash("senha123"),
            tenant_id=tenant.id,
            role="patient"
        )

        patient2 = models.User(
            name="Carlos Oliveira",
            email="carlos@email.com",
            password_hash=generate_password_hash("senha123"),
            tenant_id=tenant.id,
            role="patient"
        )

        db.add_all([doctor, patient1, patient2])
        db.commit()

        print("✅ Banco de dados populado com sucesso!")
        print(f"\n📊 Dados criados:")
        print(f"   Tenant: {tenant.name} (ID: {tenant.id})")
        print(f"   Usuários: {len([doctor, patient1, patient2])}")
        print(f"\n🔐 Credenciais de teste:")
        print(f"   Médico: doctor@clinic.com / senha123")
        print(f"   Paciente 1: maria@email.com / senha123")
        print(f"   Paciente 2: carlos@email.com / senha123")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
