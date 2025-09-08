import pytest


@pytest.mark.asyncio
async def test_health_v1(client):
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_v2(client):
    r = await client.get("/api/v2/health")
    assert r.status_code == 200
    assert r.json()["version"] == 2


@pytest.mark.asyncio
async def test_login(client):
    r = await client.post("/api/v1/login", json={"username": "alice"})
    assert r.status_code == 200
    assert r.json()["token"] == "alice"
