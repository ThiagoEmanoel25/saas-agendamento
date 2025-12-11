from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Appointment
import logging
from datetime import datetime
from typing import Any, Dict
from marshmallow import Schema, fields, ValidationError
from sqlalchemy import func

# configuração de logging
logger = logging.getLogger(__name__)
appointment_bp = Blueprint('appointments',__name__, url_prefix='/appointments')

# schema para validação de dados de agendamento
class AppointmentSchema(Schema):
    tenant_id = fields.Int(required=True)
    patient_id = fields.Int(required=True)
    doctor_id = fields.Int(required=True)
    start_datetime = fields.DateTime(required=True)
    end_datetime = fields.DateTime(required=True)
    notes = fields.Str(required=False, allow_none=True)

    class Meta:
        strict = True

@appointment_bp.route('/', methods=['POST'])
def create_appointment() -> tuple:
    try:

        data = request.get_json() or {}
        schema = AppointmentSchema()

        # Valida os dados de entrada
        try:
            validated_data: Dict[str, Any] = schema.load(data)  # type: ignore
        except ValidationError as err:
            return jsonify({"error": "Dados inválidos", "details": err.messages}), 400

        # Extrair dados validados (Type Safety)
        doctor_id: int = validated_data['doctor_id']
        patient_id: int = validated_data['patient_id']
        start_datetime: datetime = validated_data["start_datetime"]
        end_datetime: datetime = validated_data["end_datetime"]
        tenant_id: int = validated_data["tenant_id"]

        existing_appointment = db.session.execute(
            db.select(Appointment).where(
                Appointment.doctor_id == doctor_id,

                Appointment.start_datetime < end_datetime,
                Appointment.end_datetime > start_datetime,
                Appointment.tenant_id == tenant_id
            )
        ).scalar_one_or_none()

        if existing_appointment:
            return jsonify({
                "error": "Conflito de horário",
                "message": "O médico já tem um agendamento nesse horário."
            }), 409

        # Criar agendamento
        appointment = Appointment()
        appointment.tenant_id = tenant_id
        appointment.patient_id = patient_id
        appointment.doctor_id = doctor_id
        appointment.start_datetime = start_datetime
        appointment.end_datetime = end_datetime
        appointment.notes = validated_data.get('notes')
        appointment.status = 'scheduled'

        db.session.add(appointment)
        db.session.commit()

        return jsonify({
            'message': 'Agendamento criado com sucesso', # Corrigido de 'massage' para 'message'
            'appointment': {
                'id': appointment.id,
                'patient_id': appointment.patient_id,
                'doctor_id': appointment.doctor_id,
                'start_datetime': appointment.start_datetime.isoformat(),
                'end_datetime': appointment.end_datetime.isoformat(),
                'status': appointment.status
            }
        }), 201


    except Exception as e:

        db.session.rollback()
        logger.error(f"Erro ao criar agendamento: {str(e)}", exc_info=True)
        return jsonify({'error': 'Erro interno do servidor'}), 500

@appointment_bp.route('/', methods=['GET'])
def list_appointments() -> tuple:
    try:
# obter parâmetros da requisição
        doctor_id = request.args.get('doctor_id', type=int)
        date_str = request.args.get('date', type=str)
# inicia a construção da query
        query = db.select(Appointment)
# aplicamos o filtro por doctor_id se fornecido
        if doctor_id:
            query = query.where(Appointment.doctor_id == doctor_id)

        if date_str:
            try:

                filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()

                query = query.where(db.func.date(Appointment.start_datetime) == filter_date)
            except ValueError:
                return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD.'}), 400

# ordena os resultados por data e hora de início
        query = query.order_by(Appointment.start_datetime)

        appointments = db.session.execute(query).scalars().all()

        Schema = AppointmentSchema(many=True)

        result = Schema.dump(appointments)

        return jsonify({'appointments': result}), 200

    except Exception as e:

        logger.error(f"Erro ao listar agendamentos: {str(e)}", exc_info=True)
        return jsonify({'error': 'Erro interno do servidor'}), 500