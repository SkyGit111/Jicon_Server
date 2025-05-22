# tests/test_admin_routes.py

import pytest

@pytest.mark.parametrize("payload, status_code", [
    ({}, 400),  # 缺少字段
    ({"name": "a", "email": "x", "password": "p"}, 400),  # email 格式无效
    ({"name": "alice", "email": "alice@example.com"}, 400),  # 缺少 password
])
def test_signup_validation(client, payload, status_code):
    """注册接口对非法输入返回 400"""
    resp = client.post("/admin/signup", json=payload)
    assert resp.status_code == status_code

def test_full_admin_flow(client):
    """
    完整流程：
      1) 注册管理员
      2) 登录并拿到 token
      3) 用 token 调受保护接口：列表、创建第二账号、查询、更新、改密、禁用、删除
    """
    # 1. 注册第一个管理员
    signup_data = {
        "name": "alice",
        "email": "alice@example.com",
        "password": "password123"
    }
    resp = client.post("/admin/signup", json=signup_data)
    assert resp.status_code == 201
    admin1 = resp.get_json()
    admin1_id = admin1["id"]

    # 2. 登录拿 token
    resp = client.post("/admin/signin", json={
        "email": "alice@example.com",
        "password": "password123"
    })
    assert resp.status_code == 200
    token = resp.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. GET /admin/ 列表，应只有一个
    resp = client.get("/admin/", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 1

    # 4. POST /admin/ 创建第二个管理员
    resp = client.post("/admin/", headers=headers, json={
        "name": "bob",
        "email": "bob@example.com",
        "password": "pwd456"
    })
    assert resp.status_code == 201
    admin2_id = resp.get_json()["id"]

    # 5. GET /admin/{id}
    resp = client.get(f"/admin/{admin2_id}", headers=headers)
    assert resp.status_code == 200

    # 6. PUT /admin/{id}
    resp = client.put(f"/admin/{admin2_id}", headers=headers, json={
        "name": "bob2", "email": "bob2@example.com"
    })
    assert resp.status_code == 200

    # 7. PUT /admin/{id}/password
    resp = client.put(f"/admin/{admin2_id}/password", headers=headers, json={
        "password": "newpwd789"
    })
    assert resp.status_code == 200

    # 8. PUT /admin/{id}/disable
    resp = client.put(f"/admin/{admin2_id}/disable", headers=headers)
    assert resp.status_code == 200

    # 9. 禁用后尝试登录，应该 401
    resp = client.post("/admin/signin", json={
        "email": "bob2@example.com",
        "password": "newpwd789"
    })
    assert resp.status_code == 401

    # 10. DELETE /admin/{id}
    resp = client.delete(f"/admin/{admin2_id}", headers=headers)
    assert resp.status_code == 200

    # 11. 再次列表，应只剩 alice
    resp = client.get("/admin/", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["total"] == 1

@pytest.mark.parametrize("method, endpoint", [
    ("get",    "/admin/"),
    ("get",    "/admin/1"),
    ("post",   "/admin/"),            # 创建接口也受保护
    ("put",    "/admin/1"),
    ("put",    "/admin/1/password"),
    ("put",    "/admin/1/disable"),
    ("delete", "/admin/1"),
])
def test_protected_requires_auth(client, method, endpoint):
    """
    未带 token 调用任何受保护的接口，都应返回 401。
    """
    resp = getattr(client, method)(endpoint, json={})
    assert resp.status_code == 401
