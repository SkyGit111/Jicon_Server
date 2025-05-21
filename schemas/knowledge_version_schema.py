from marshmallow import Schema, fields, validate

class KnowledgeVersionSchema(Schema):
    id          = fields.Int(dump_only=True)
    version     = fields.Str(required=True, validate=validate.Length(max=50))
    description = fields.Str(validate=validate.Length(max=255))
    created_at  = fields.DateTime(dump_only=True)
