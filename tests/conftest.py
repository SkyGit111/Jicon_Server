# tests/conftest.py

import os
import sys
import pytest

# ── 确保项目根目录在 sys.path 中 ───────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from extensions import db as _db
from flask_jwt_extended import create_access_token

@pytest.fixture(scope="function")
def app():
    """
    为每个测试函数创建一个全新的 Flask 应用实例，
    使用 SQLite 内存库，保证数据隔离。
    """
    os.environ["FLASK_ENV"] = "testing"
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    # 如果 create_app 中有向量库加载，可以通过该配置跳过
    app.config["VECTOR_DB_DISABLE_INIT"] = True

    with app.app_context():
        _db.create_all()
    yield app
    with app.app_context():
        _db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    """
    Flask 测试客户端，用于发起 HTTP 请求。
    """
    return app.test_client()

@pytest.fixture(scope="function")
def access_token(app):
    """
    在测试环境中，使用 flask_jwt_extended 生成一个有效的 JWT，
    供后续调用需要认证的接口时使用。
    """
    # identity 可按需设：如管理员 id、用户名等
    return create_access_token(identity="test_user")

@pytest.fixture(scope="function")
def auth_client(client, access_token):
    """
    基于 client，自动在每次请求中带上 Authorization 头，
    免去每次手动设置，模拟“拿 token → 调接口”全流程。
    """
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
    return client
