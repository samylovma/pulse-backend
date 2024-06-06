from litestar import Litestar
from litestar.status_codes import HTTP_400_BAD_REQUEST
from litestar.testing import AsyncTestClient


async def test_invalid_region(client: AsyncTestClient[Litestar]) -> None:
    response = await client.get("/api/countries", params={"region": "utopia"})
    assert response.status_code == HTTP_400_BAD_REQUEST


async def test_empty_region(client: AsyncTestClient[Litestar]) -> None:
    response = await client.get("/api/countries", params={"region": ""})
    assert response.status_code == HTTP_400_BAD_REQUEST
