from litestar.status_codes import HTTP_200_OK
from litestar.testing import AsyncTestClient

from pulse_backend.app import create_app


async def test_ping() -> None:
    async with AsyncTestClient(create_app()) as client:
        response = await client.get("/api/ping")
        assert response.status_code == HTTP_200_OK
        assert response.text == "ok"
