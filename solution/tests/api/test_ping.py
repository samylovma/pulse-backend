from litestar import Litestar
from litestar.status_codes import HTTP_200_OK
from litestar.testing import AsyncTestClient


async def test_ping(client: AsyncTestClient[Litestar]) -> None:
    response = await client.get("/api/ping")
    assert response.status_code == HTTP_200_OK
    assert response.text == "ok"
