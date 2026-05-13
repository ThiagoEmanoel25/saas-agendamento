from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Appointment, User
from pydantic import ValidationError
from app.schemas import AppointmentSchema
from datetime import datetime

appointments_bp = Blueprint('appointments', __name__)


@appointments_bp.route('/', methods=['POST'])
@jwt_required()
def create_appointment():
    """Create a new appointment"""
    try:
        data = AppointmentSchema(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    current_user_id = get_jwt_identity()
    
    try:
        appointment = Appointment(
            doctor_id=data.doctor_id,
            patient_id=current_user_id,
            appointment_date=datetime.fromisoformat(data.appointment_date),
            start_time=data.start_time,
            end_time=data.end_time,
            tenant_id=request.json.get('tenant_id', 1),
            status=data.status
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            "id": appointment.id,
            "status": appointment.status,
            "message": "Appointment created successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@appointments_bp.route('/<int:appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment(appointment_id):
    """Get appointment details"""
    try:
        appointment = Appointment.query.get(appointment_id)
        
        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404
        
        return jsonify({
            "id": appointment.id,
            "doctor_id": appointment.doctor_id,
            "patient_id": appointment.patient_id,
            "appointment_date": str(appointment.appointment_date),
            "start_time": str(appointment.start_time),
            "end_time": str(appointment.end_time),
            "status": appointment.status,
            "created_at": str(appointment.created_at)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def parse_time(value: str):
    from datetime import datetime as _dt, time as _time
    if value is None:
        return None
    if isinstance(value, _time):
        return value
    try:
        return _dt.fromisoformat(value).time()
    except Exception:
        pass
    for fmt in ('%H:%M', '%H:%M:%S', '%H:%M:%S.%f'):
        try:
            return _dt.strptime(value, fmt).time()
        except Exception:
            continue
    raise ValueError("Invalid time format. Use 'HH:MM' or 'HH:MM:SS'")


@appointments_bp.route('/<int:appointment_id>', methods=['PATCH'])
@jwt_required()
def update_appointment(appointment_id):
    """Update appointment (date, times, doctor, status)"""
    try:
        from pydantic import BaseModel, ValidationError as PydValidationError
        from typing import Optional

        class AppointmentUpdateSchema(BaseModel):
            doctor_id: Optional[int] = None
            appointment_date: Optional[str] = None
            start_time: Optional[str] = None
            end_time: Optional[str] = None
            status: Optional[str] = None
            tenant_id: Optional[int] = None

        payload = request.json or {}
        try:
            data = AppointmentUpdateSchema(**payload)
        except PydValidationError as e:
            return jsonify({"error": e.errors()}), 400

        current_user_id = get_jwt_identity()
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404

        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.role != 'admin' and current_user_id not in (appointment.patient_id, appointment.doctor_id):
            return jsonify({"error": "Not authorized to update this appointment"}), 403

        new_date = appointment.appointment_date
        new_start = appointment.start_time
        new_end = appointment.end_time
        new_doctor = appointment.doctor_id

        if data.appointment_date is not None:
            try:
                new_date = datetime.fromisoformat(data.appointment_date)
            except Exception:
                return jsonify({"error": "Invalid appointment_date format. Use YYYY-MM-DD or ISO format"}), 400

        if data.start_time is not None:
            try:
                new_start = parse_time(data.start_time)
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

        if data.end_time is not None:
            try:
                new_end = parse_time(data.end_time)
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

        if data.doctor_id is not None:
            new_doctor = data.doctor_id

        if new_start >= new_end:
            return jsonify({"error": "start_time must be before end_time"}), 400

        conflict = Appointment.query.filter(
            Appointment.doctor_id == new_doctor,
            Appointment.appointment_date == new_date,
            Appointment.id != appointment_id,
            Appointment.status != 'canceled',
            Appointment.start_time < new_end,
            Appointment.end_time > new_start
        ).first()
        if conflict:
            return jsonify({"error": "Scheduling conflict for selected time"}), 400

        appointment.appointment_date = new_date
        appointment.start_time = new_start
        appointment.end_time = new_end
        appointment.doctor_id = new_doctor
        if data.status is not None:
            appointment.status = data.status
        if data.tenant_id is not None:
            appointment.tenant_id = data.tenant_id

        db.session.commit()
        return jsonify({
            "id": appointment.id,
            "status": appointment.status,
            "message": "Appointment updated successfully"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@appointments_bp.route('/<int:appointment_id>/cancel', methods=['PATCH', 'DELETE'])
@jwt_required()
def cancel_appointment(appointment_id):
    """Cancel appointment (sets status to 'canceled')"""
    try:
        current_user_id = get_jwt_identity()
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404

        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.role != 'admin' and current_user_id not in (appointment.patient_id, appointment.doctor_id):
            return jsonify({"error": "Not authorized to cancel this appointment"}), 403

        if appointment.status == 'canceled':
            return jsonify({"id": appointment.id, "status": appointment.status, "message": "Already canceled"}), 200

        appointment.status = 'canceled'
        db.session.commit()
        return jsonify({
            "id": appointment.id,
            "status": appointment.status,
            "message": "Appointment canceled"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@appointments_bp.route('/', methods=['GET'])
@jwt_required()
def list_appointments():
    """List all appointments for the current user"""
    try:
        current_user_id = get_jwt_identity()
        
        appointments = Appointment.query.filter(
            (Appointment.patient_id == current_user_id) | 
            (Appointment.doctor_id == current_user_id)
        ).all()
        
        return jsonify({
            "appointments": [
                {
                    "id": apt.id,
                    "doctor_id": apt.doctor_id,
                    "patient_id": apt.patient_id,
                    "appointment_date": str(apt.appointment_date),
                    "status": apt.status
                }
                for apt in appointments
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
