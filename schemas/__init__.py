# schemas/__init__.py

from flask import jsonify
from marshmallow import Schema

def _schema_jsonify(self, obj):
    """
    将 obj 先用 marshmallow dump，再用 Flask jsonify 返回
    """
    data = self.dump(obj)
    return jsonify(data)

# 把 jsonify 方法注入到所有 Schema
Schema.jsonify = _schema_jsonify

# 导入所有具体的 Schema 类，保证补丁加载
from .admin_schema             import AdminSchema
from .detection_schema         import DetectionSchema
from .knowledge_version_schema import KnowledgeVersionSchema
from .message_schema           import MessageSchema
from .model_version_schema     import ModelVersionSchema
from .result_schema            import ResultSchema
from .terminal_schema          import TerminalSchema
from .user_group_schema        import UserGroupSchema

__all__ = [
    "AdminSchema",
    "DetectionSchema",
    "KnowledgeVersionSchema",
    "MessageSchema",
    "ModelVersionSchema",
    "ResultSchema",
    "TerminalSchema",
    "UserGroupSchema"
]
