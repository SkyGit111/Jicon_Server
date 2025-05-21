from marshmallow import Schema, fields, validate
from datetime import datetime

def validate_datetime(value):
    try:
        datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    except Exception:
        raise ValueError('日期格式必须为 YYYY-MM-DD HH:MM:SS')

class TerminalSchema(Schema):
    id = fields.Int(dump_only=True)
    signin_date = fields.Str(required=True, validate=validate_datetime)
    state = fields.Bool(required=True)
    group_id = fields.Int(required=True)
    group_name = fields.Str(dump_only=True)
