from marshmallow import Schema, fields, validate, ValidationError

class AdminSchema(Schema):
    id       = fields.Int(dump_only=True)
    name     = fields.Str(required=True, validate=validate.Length(max=20))
    email    = fields.Email(required=True, validate=validate.Length(max=30))
    password = fields.Str(load_only=True, required=True, validate=validate.Length(min=6))
    disabled = fields.Bool(dump_only=True)
