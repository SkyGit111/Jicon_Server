# extensions/__init__.py

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# ORM
db = SQLAlchemy()
# JWT
jwt = JWTManager()
# CORS 实例
cors = CORS()

def init_extensions(app):
    """
    初始化所有第三方扩展：
      - SQLAlchemy
      - JWTManager
      - CORS
    """
    db.init_app(app)
    jwt.init_app(app)
    # 允许所有来源，也可根据 Config.CORS_ORIGINS 做更细粒度控制
    cors.init_app(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})
