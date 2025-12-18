from marshmallow import schema, fields, validate

class availabilitySchema(schema.Schema):
    #id e doctor_id são 'dump_only' para porque o usuário não envia isso

    id = fields.Int(dump_only=True)
    doctor_id = fields.Int(dump_only=True)

    day_of_week = fields.Int(required=True, validate=validate.Range(min=0, max=6))

    start_time = fields.Time(required=True)
    end_time = fields.Time(required=True)

    slot_duration = fields.Int(load_default=30, validate=validate.Range(min=5))


