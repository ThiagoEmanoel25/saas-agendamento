from app import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Integer, Boolean, DateTime, Time, Text
from datetime import datetime


class TenantAwareModel(db.Model):
    __abstract__ = True  # Diz ao SQLAlchemy: "Não crie uma tabela para esta classe, ela é só um modelo"

    # Todos que herdarem disso terão essa coluna automaticamente
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenant.id'), nullable=False)


class Tenant(db.Model): # modelo para representar os tenants
    __tablename__ = 'tenant'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    subdomain: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class User(TenantAwareModel):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)

    role: Mapped[str] = mapped_column(String(20), default='patient')  # e.g., 'admin', 'customer'


class DoctorAvailavility(TenantAwareModel):
    __tablename__ = 'doctor_availability'
    id: Mapped[int] = mapped_column(primary_key=True)

    doctor_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time: Mapped[Time] = mapped_column(Time, nullable=False)
    end_time: Mapped[Time] = mapped_column(Time, nullable=False)

    slot_duration: Mapped[int] = mapped_column(Integer, default=30)  # duração do slot em minutos

class Appointment(TenantAwareModel): # herança de TenantAwareModel
    __tablename__ = 'appointment'
    id: Mapped[int] = mapped_column(primary_key=True)

    patient_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    Doctor_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    notes: Mapped[str] = mapped_column(Text,nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='scheduled')  # e.g., 'scheduled', 'completed', 'canceled'
