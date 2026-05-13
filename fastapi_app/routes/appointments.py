from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi_app import models, schemas
from fastapi_app.db import get_db
from fastapi_app.auth import get_current_user

router = APIRouter()


@router.post('/', response_model=schemas.AppointmentOut, status_code=201)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    """Create a new appointment"""
    # conflict check
    conflict = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == appointment.doctor_id,
        models.Appointment.appointment_date == appointment.appointment_date,
        models.Appointment.status != 'canceled',
        models.Appointment.start_time < appointment.end_time,
        models.Appointment.end_time > appointment.start_time
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="Scheduling conflict for selected time")

    db_obj = models.Appointment(
        doctor_id=appointment.doctor_id,
        patient_id=user.id,
        appointment_date=appointment.appointment_date,
        start_time=appointment.start_time,
        end_time=appointment.end_time,
        tenant_id=appointment.tenant_id,
        status=appointment.status
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.get('/{appointment_id}', response_model=schemas.AppointmentOut)
def get_appointment(appointment_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    apt = db.query(models.Appointment).get(appointment_id)
    if not apt:
        raise HTTPException(status_code=404, detail='Appointment not found')
    if user.role != 'admin' and user.id not in (apt.patient_id, apt.doctor_id):
        raise HTTPException(status_code=403, detail='Not authorized')
    return apt


@router.get('/', response_model=List[schemas.AppointmentOut])
def list_appointments(db: Session = Depends(get_db), user = Depends(get_current_user)):
    apts = db.query(models.Appointment).filter(
        (models.Appointment.patient_id == user.id) | (models.Appointment.doctor_id == user.id)
    ).all()
    return apts


@router.patch('/{appointment_id}')
def update_appointment(appointment_id: int, payload: schemas.AppointmentUpdate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    apt = db.query(models.Appointment).get(appointment_id)
    if not apt:
        raise HTTPException(status_code=404, detail='Appointment not found')
    if user.role != 'admin' and user.id not in (apt.patient_id, apt.doctor_id):
        raise HTTPException(status_code=403, detail='Not authorized')

    new_date = apt.appointment_date
    new_start = apt.start_time
    new_end = apt.end_time
    new_doctor = apt.doctor_id

    if payload.appointment_date is not None:
        new_date = payload.appointment_date
    if payload.start_time is not None:
        new_start = payload.start_time
    if payload.end_time is not None:
        new_end = payload.end_time
    if payload.doctor_id is not None:
        new_doctor = payload.doctor_id

    if new_start >= new_end:
        raise HTTPException(status_code=400, detail='start_time must be before end_time')

    conflict = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == new_doctor,
        models.Appointment.appointment_date == new_date,
        models.Appointment.id != appointment_id,
        models.Appointment.status != 'canceled',
        models.Appointment.start_time < new_end,
        models.Appointment.end_time > new_start
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail='Scheduling conflict for selected time')

    apt.appointment_date = new_date
    apt.start_time = new_start
    apt.end_time = new_end
    apt.doctor_id = new_doctor
    if payload.status is not None:
        apt.status = payload.status
    if payload.tenant_id is not None:
        apt.tenant_id = payload.tenant_id

    db.commit()
    db.refresh(apt)
    return {"id": apt.id, "status": apt.status, "message": "Appointment updated successfully"}


@router.patch('/{appointment_id}/cancel')
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    apt = db.query(models.Appointment).get(appointment_id)
    if not apt:
        raise HTTPException(status_code=404, detail='Appointment not found')
    if user.role != 'admin' and user.id not in (apt.patient_id, apt.doctor_id):
        raise HTTPException(status_code=403, detail='Not authorized')
    if apt.status == 'canceled':
        return {"id": apt.id, "status": apt.status, "message": "Already canceled"}
    apt.status = 'canceled'
    db.commit()
    db.refresh(apt)
    return {"id": apt.id, "status": apt.status, "message": "Appointment canceled"}
