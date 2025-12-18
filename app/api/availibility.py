from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import DoctorAvailability
from app.schema import availibilitySchema
from flask_jwt_extended import jwt_required, get_jwt_identity

availibility_bp = Blueprint('availibility', __name__, url_prefix='/api/availibility')

@availibility_bp.route('/', methods=['POST'])
@jwt_required()

def create_availibility():

    data = request.get_json() or {}

    schema = availibilitySchema()
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400

    current_user_id = int(get_jwt_identity())

    availibility = DoctorAvailability(
        doctor_id=current_user_id,
        tenant_id=1,
        day_of_week=data['day_of_week'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        slot_duration=data.get('slot_duration', 30)
    )

    try:
        db.session.add(availibility)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Erro ao salvar disponibilidade", "details": str(e)}), 500

    return jsonify(schema.dump(availibility)), 201

@availibility_bp.route('/', methods=['GET'])
@jwt_required()

def list_availibilities():
    current_user_id = int(get_jwt_identity())

    intems = db.session.execute(
        db.select(DoctorAvailability).where(DoctorAvailability.doctor_id == current_user_id)
    ).scalars().all()

    return jsonify(availibilitySchema(many=True).dump(intems)), 200