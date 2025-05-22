# tests/test_units.py

import pytest
from marshmallow import ValidationError
from datetime import datetime

from schemas import AdminSchema
from models.message   import Message
from models.detection import Detection

def test_admin_schema_load_valid():
    schema = AdminSchema()
    data = {"name": "test", "email": "test@example.com", "password": "pass123"}
    result = schema.load(data)
    assert result["name"] == "test"
    assert result["email"] == "test@example.com"
    assert result["password"] == "pass123"

@pytest.mark.parametrize("invalid", [
    {},  # 全部缺失
    {"name": "a", "email": "x", "password": "p"},  # email/密码格式不符
    {"name": "user", "email": "not-an-email", "password": "password"},
])
def test_admin_schema_load_invalid(invalid):
    schema = AdminSchema()
    with pytest.raises(ValidationError):
        schema.load(invalid)

def test_message_to_dict():
    msg = Message(id=1, content="hello world", label="info")
    out = msg.to_dict()
    assert out == {"id": 1, "content": "hello world", "label": "info"}

def test_detection_to_dict():
    dt = datetime(2025, 5, 22, 15, 30, 0)
    det = Detection(
        id=2,
        date=dt,
        message_id=1,
        type="文本",
        terminal_id=3
    )
    out = det.to_dict()
    assert out == {
        "id": 2,
        "date": "2025-05-22 15:30:00",
        "message_id": 1,
        "type": "文本",
        "terminal_id": 3
    }
