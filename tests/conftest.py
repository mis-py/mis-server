
import pytest
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager
from typing import AsyncGenerator
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager

from main import app

ClientManagerType = AsyncGenerator[AsyncClient, None]

@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def client() -> ClientManagerType:
    app.state.testing = True
    async with LifespanManager(app, startup_timeout=60, shutdown_timeout=60) as manager:
        transport = ASGITransport(app=manager.app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c
