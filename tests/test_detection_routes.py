# tests/test_detection_routes.py

import pytest
import routes.detection_routes as dr  # 导入路由模块以便打桩

@pytest.fixture(autouse=True)
def mock_detect(monkeypatch):
    """
    在路由模块里打桩 detect_core，避免调用真实向量/模型。
    """
    monkeypatch.setattr(dr, "detect_core", lambda text: [{"label": "模拟"}])
    yield

def test_detect_text_only(auth_client):
    """
    测试 /detections/detect 接口，只做文本检测，不落库。
    """
    resp = auth_client.post("/detections/detect", json={"text": "hello"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["text"] == "hello"
    # 只校验 label
    assert isinstance(data["results"], list)
    assert data["results"][0]["label"] == "模拟"

def test_create_and_get_detection(auth_client):
    """
    测试完整的检测创建 + 查询流程，需要先创建 UserGroup 和 Terminal。
    """
    # 1) 新建用户组
    rg = auth_client.post("/user_groups/", json={"name": "g1"})
    assert rg.status_code == 201
    group_id = rg.get_json()["id"]

    # 2) 新建终端（必须带 group_id）
    rt = auth_client.post("/terminals/", json={
        "signin_date": "2025-05-22 12:00:00",
        "state": True,
        "group_id": group_id
    })
    assert rt.status_code == 201
    terminal_id = rt.get_json()["id"]

    # 3) 创建检测任务
    rd = auth_client.post("/detections/", json={
        "text": "测试文本",
        "type": "文本",
        "terminal_id": terminal_id
    })
    assert rd.status_code == 201
    payload = rd.get_json()

    # 检查检测记录
    det = payload["detection"]
    assert det["type"] == "文本"
    det_id = det["id"]

    # 检查检测结果只包含 label
    results = payload["results"]
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["label"] == "模拟"

    # 4) 按 ID 查询
    rg2 = auth_client.get(f"/detections/{det_id}")
    assert rg2.status_code == 200
    fetched = rg2.get_json()
    assert fetched["id"] == det_id
    assert fetched["type"] == "文本"
