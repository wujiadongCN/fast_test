import pytest


def auth_hdr(u: str):
    return {"Authorization": f"Bearer {u}"}


@pytest.mark.asyncio
async def test_create_get_delete_item(client):
    # 创建
    r = await client.post(
        "/api/v1/items",
        json={"name": "Apple", "price": 3.5},
        headers=auth_hdr("alice"),
    )
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == 1
    assert data["owner"] == "alice"

    # 获取
    r2 = await client.get("/api/v1/items/1", headers=auth_hdr("alice"))
    assert r2.status_code == 200
    assert r2.json()["name"] == "Apple"

    # 删除
    r3 = await client.delete("/api/v1/items/1", headers=auth_hdr("alice"))
    assert r3.status_code == 200
    assert r3.json()["deleted"] is True

    # 再获取应 404
    r4 = await client.get("/api/v1/items/1", headers=auth_hdr("alice"))
    assert r4.status_code == 404


@pytest.mark.asyncio
async def test_validation_and_422_shape(client):
    # price <= 0 触发校验错误
    r = await client.post(
        "/api/v1/items",
        json={"name": "A", "price": 0},
        headers=auth_hdr("bob"),
    )
    assert r.status_code == 422
    body = r.json()
    assert body["code"] == 10001
    assert body["message"] == "validation error"
    assert isinstance(body["errors"], list)
    assert body["path"].startswith("/api/v1")


@pytest.mark.asyncio
async def test_pagination_and_header_params(client):
    # 先创建 3 条
    for i in range(3):
        await client.post(
            "/api/v1/items",
            json={"name": f"N{i}", "price": 1.0 + i},
            headers=auth_hdr("carl"),
        )

    # 取第 2 条开始的 2 条
    r = await client.get(
        "/api/v1/items",
        headers={**auth_hdr("carl"), "limit": "2", "offset": "1"},
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    assert [it["name"] for it in data] == ["N1", "N2"]