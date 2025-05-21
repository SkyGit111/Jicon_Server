from marshmallow import Schema, fields, validate
from datetime import datetime

def validate_type(value):
    if value not in ('文本', '语音', '综合', 'text', 'audio', 'mixed'):
        raise ValueError('type 必须为 “文本”/“语音”/“综合” 或对应英文')

def validate_datetime(value):
    try:
        datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    except Exception:
        raise ValueError('日期格式必须为 YYYY-MM-DD HH:MM:SS')

class DetectionSchema(Schema):
    id          = fields.Int(dump_only=True)
    date        = fields.Str(validate=validate_datetime)
    message_id  = fields.Int(required=True)
    type        = fields.Str(required=True, validate=validate_type)
    terminal_id = fields.Int(required=True)
