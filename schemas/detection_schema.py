from marshmallow import Schema, fields, validate
from datetime import datetime

def validate_datetime(value):
    try:
        datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    except Exception:
        raise ValueError('日期格式必须为 YYYY-MM-DD HH:MM:SS')

class DetectionSchema(Schema):
    id          = fields.Int(dump_only=True)
    date        = fields.Str(validate=validate_datetime)
    message_id  = fields.Int(required=True)
    # 🔴 删去 type 字段
    # type        = fields.Str(required=True)

    # 🟢 新增：prob 与 label 字段
    prob        = fields.Float(required=True)
    label       = fields.Str(required=True, validate=validate.Length(min=1))

    terminal_id = fields.Int(required=True)
