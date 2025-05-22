# tests/test_message_routes.py

import pytest

def test_message_crud_and_statistics(auth_client):
    # 1) 创建一条消息
    resp = auth_client.post("/messages/", json={"content": "hi", "label": "test"})
    assert resp.status_code == 201
    msg = resp.get_json()
    mid = msg["id"]
    assert msg["content"] == "hi"
    assert msg["label"] == "test"

    # 2) 获取详情
    resp = auth_client.get(f"/messages/{mid}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == mid

    # 3) 更新
    resp = auth_client.put(f"/messages/{mid}", json={"content": "hello", "label": "info"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["content"] == "hello"
    assert data["label"] == "info"

    # 4) 再创建一条同 label 消息
    resp = auth_client.post("/messages/", json={"content": "another", "label": "info"})
    assert resp.status_code == 201

    # 5) 统计接口
    resp = auth_client.get("/messages/statistics")
    assert resp.status_code == 200
    stats = resp.get_json()["statistics"]
    info_stat = next((e for e in stats if e["label"] == "info"), None)
    assert info_stat is not None
    assert info_stat["count"] == 2  # 两条 info

    # 6) 列表接口
    resp = auth_client.get("/messages/")
    assert resp.status_code == 200
    listing = resp.get_json()
    assert listing["total"] == 2
    assert isinstance(listing["items"], list)

    # 7) 删除第一条
    resp = auth_client.delete(f"/messages/{mid}")
    assert resp.status_code == 200

    # 8) 列表应剩 1 条
    resp = auth_client.get("/messages/")
    assert resp.get_json()["total"] == 1
