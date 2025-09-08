import pytest
from httpx import AsyncClient, ASGITransport
from app.main import create_app
from app.services import clear_state


@pytest.fixture(autouse=True)
async def _clear_state():
    # 每个测试前清理内存 DB
    clear_state()
    yield


@pytest.fixture()
async def client():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac