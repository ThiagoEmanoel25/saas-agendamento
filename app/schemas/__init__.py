from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime, time


class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str
    name: str
    tenant_id: int

    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class AppointmentSchema(BaseModel):
    doctor_id: int
    patient_id: int
    appointment_date: str
    start_time: str
    end_time: str
    status: Optional[str] = 'pending'


class DoctorAvailabilitySchema(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time
    slot_duration: Optional[int] = 30