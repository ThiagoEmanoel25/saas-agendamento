from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Integer, Boolean, DateTime, Time, Text
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash



class TenantAwareModel(db.Model):
    __abstract__ = True  # Diz ao SQLAlchemy: "Não crie uma tabela para esta classe, ela é só um modelo"

    # Todos que herdarem disso terão essa coluna automaticamente
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenant.id'), nullable=False)


class Tenant(db.Model): # modelo para representar os tenants
    __tablename__ = 'tenant'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=100), nullable=False)
    subdomain: Mapped[str] = mapped_column(String(length=50), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)

class User(TenantAwareModel):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=100), nullable=False)
    email: Mapped[str] = mapped_column(String(length=120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(length=255), nullable=False)

    def check_password(self, password: str) -> bool:
        """Retorna True se a senha estiver correta, False se estiver incorreta"""
        return check_password_hash(self.password_hash, password)

    role: Mapped[str] = mapped_column(String(length=20), default='patient')  # e.g., 'admin', 'customer'


class DoctorAvailability(TenantAwareModel):
    __tablename__ = 'doctor_availability'
    id: Mapped[int] = mapped_column(primary_key=True)

    doctor_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    day_of_week: Mapped[int] = mapped_column(Integer(), nullable=False)  # 0=Monday, 6=Sunday
    start_time: Mapped[Time] = mapped_column(Time(), nullable=False)
    end_time: Mapped[Time] = mapped_column(Time(), nullable=False)

    slot_duration: Mapped[int] = mapped_column(Integer(), default=30)  # duração do slot em minutos

    def __init__(self, doctor_id: int, tenant_id: int, day_of_week: int, start_time, end_time, slot_duration: int = 30):
        self.doctor_id = doctor_id
        self.tenant_id = tenant_id
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.slot_duration = slot_duration

class Appointment(TenantAwareModel): # herança de TenantAwareModel
    __tablename__ = 'appointment'
    id: Mapped[int] = mapped_column(primary_key=True)

    patient_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    start_datetime: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(), nullable=False)

    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str] = mapped_column(String(length=20), default='scheduled')  # e.g., 'scheduled', 'completed', 'canceled'

