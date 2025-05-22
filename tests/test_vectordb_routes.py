# tests/test_vectordb_routes.py

import pytest
import routes.vectordb_routes as vr


@pytest.mark.parametrize("state, expected", [
    (None, False),          # 默认 vector_db 初始值
    (object(), True),       # 模拟已加载
])
def test_status(auth_client, monkeypatch, state, expected):
    """
    GET /vectordb/status 返回当前 vector_db 是否已加载。
    """
    monkeypatch.setattr(vr, "vector_db", state, raising=False)
    resp = auth_client.get("/vectordb/status")
    assert resp.status_code == 200
    assert resp.get_json() == {"loaded": expected}


def test_reload_success(auth_client, monkeypatch):
    """
    POST /vectordb/reload 成功时返回 {"status":"reloaded"}.
    """
    called = {}
    def fake_reload():
        called['ok'] = True
    monkeypatch.setattr(vr, "reload_vdb", fake_reload)
    resp = auth_client.post("/vectordb/reload")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "reloaded"}
    assert called.get('ok', False) is True


def test_reload_failure(auth_client, monkeypatch):
    """
    POST /vectordb/reload 异常时返回 500 和 error 字段。
    """
    def fake_reload():
        raise RuntimeError("oops")
    monkeypatch.setattr(vr, "reload_vdb", fake_reload)
    resp = auth_client.post("/vectordb/reload")
    assert resp.status_code == 500
    body = resp.get_json()
    assert "error" in body and "oops" in body["error"]


def test_create_success(auth_client, monkeypatch):
    """
    POST /vectordb/create 成功时返回 {"status":"created"}.
    """
    monkeypatch.setattr(vr, "create_vdb", lambda: None)
    resp = auth_client.post("/vectordb/create")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "created"}


def test_create_failure(auth_client, monkeypatch):
    """
    POST /vectordb/create 异常时返回 500 和 error 字段。
    """
    def fake_create():
        raise ValueError("fail create")
    monkeypatch.setattr(vr, "create_vdb", fake_create)
    resp = auth_client.post("/vectordb/create")
    assert resp.status_code == 500
    body = resp.get_json()
    assert "error" in body and "fail create" in body["error"]
