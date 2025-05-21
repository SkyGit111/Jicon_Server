from marshmallow import Schema, fields, validate

class ModelVersionSchema(Schema):
    id           = fields.Int(dump_only=True)
    finish_date  = fields.DateTime(dump_only=True)
    description  = fields.Str(validate=validate.Length(max=255))
    is_active    = fields.Bool(dump_only=True)
