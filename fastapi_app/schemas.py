from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime, time


class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_date: datetime
    start_time: time
    end_time: time
    tenant_id: Optional[int] = 1
    status: Optional[str] = 'pending'


class AppointmentUpdate(BaseModel):
    doctor_id: Optional[int] = None
    appointment_date: Optional[datetime] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    status: Optional[str] = None
    tenant_id: Optional[int] = None


class AppointmentOut(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    appointment_date: datetime
    start_time: time
    end_time: time
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    tenant_id: Optional[int] = 1

    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: str
    tenant_id: int

    class Config:
        orm_mode = True
