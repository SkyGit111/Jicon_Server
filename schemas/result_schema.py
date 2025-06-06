# schemas/result_schema.py
from marshmallow import Schema, fields, validate

class ResultSchema(Schema):
    id           = fields.Int(dump_only=True)
    message_id   = fields.Int(allow_none=True)
    label        = fields.Str(required=True, validate=validate.Length(max=20))
    # detection_id 这一行可删除或注释
    # detection_id = fields.Int(required=True)
    
    written      = fields.Bool(dump_only=True)   # 只输出，不让客户端填
