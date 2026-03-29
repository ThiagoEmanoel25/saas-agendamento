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
