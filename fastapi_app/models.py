from sqlalchemy import Column, Integer, String, DateTime, Time, ForeignKey, Boolean
from fastapi_app.db import Base
from datetime import datetime


class Tenant(Base):
    __tablename__ = "tenant"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    subdomain = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(20), default="patient")
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=False)


class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    slot_duration = Column(Integer, default=30)
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=False)


class Appointment(Base):
    __tablename__ = "appointment"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=False)
