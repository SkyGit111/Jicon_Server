from marshmallow import Schema, fields, validate

class UserGroupSchema(Schema):
    id        = fields.Int(dump_only=True)
    name      = fields.Str(required=True, validate=validate.Length(max=20))
    members   = fields.Str()  # 文本字段，不做长度限制
    terminal_ids = fields.List(fields.Int(), dump_only=True)
