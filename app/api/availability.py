from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import DoctorAvailability
from app.schema import availabilitySchema
from flask_jwt_extended import jwt_required, get_jwt_identity

availability_bp = Blueprint('availability', __name__, url_prefix='/api/availability')

@availability_bp.route('/', methods=['POST'])
@jwt_required()

def create_availibility():

    data = request.get_json() or {}

    schema = availabilitySchema()
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400

    current_user_id = int(get_jwt_identity())

    availability = DoctorAvailability(
        doctor_id=current_user_id,
        tenant_id=1,
        day_of_week=data['day_of_week'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        slot_duration=data.get('slot_duration', 30)
    )

    try:
        db.session.add(availability)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Erro ao salvar disponibilidade", "details": str(e)}), 500

    return jsonify(schema.dump(availability)), 201

@availability_bp.route('/', methods=['GET'])
@jwt_required()

def list_availibilities():
    current_user_id = int(get_jwt_identity())

    intems = db.session.execute(
        db.select(DoctorAvailability).where(DoctorAvailability.doctor_id == current_user_id)
    ).scalars().all()

    return jsonify(availabilitySchema(many=True).dump(intems)), 200