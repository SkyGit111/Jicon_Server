from marshmallow import Schema, fields

class MessageSchema(Schema):
    id      = fields.Int(dump_only=True)
    content = fields.Str(required=True)   # 不再限制 max length
    label   = fields.Str()
