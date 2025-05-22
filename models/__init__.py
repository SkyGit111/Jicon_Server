# models/__init__.py

# 只导入实际存在的模型类
from .admin            import Admin
from .detection        import Detection
from .knowledge_version import KnowledgeVersion
from .message          import Message
from .model_version    import ModelVersion
from .result           import Result
from .terminal         import Terminal
from .user_group       import UserGroup

# 如果未来需要 User 模型，再新建 models/user.py，然后在这里添加 import
