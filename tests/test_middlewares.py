import pytest


@pytest.mark.asyncio
async def test_request_id_and_process_time(client):
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.headers.get("X-Request-ID")
    # X-Process-Time 不是强制，但会在 TimerMiddleware 中添加
    assert r.headers.get("X-Process-Time")


@pytest.mark.asyncio
async def test_background_audit_log(client):
    # 触发创建，BackgroundTasks 写审计日志
    r = await client.post(
        "/api/v1/items",
        json={"name": "Z", "price": 9.9},
        headers={"Authorization": "Bearer zed"},
    )
    assert r.status_code == 200

    # 背景任务执行是异步调度，这里简单再访问一次确保事件循环推进
    r2 = await client.get("/api/v1/items", headers={"Authorization": "Bearer zed", "limit": "10", "offset": "0"})
    assert r2.status_code == 200

    # 直接访问内部列表进行断言（单进程测试场景）
    from app.services import AUDIT_LOG
    assert ("zed", 1) in AUDIT_LOG