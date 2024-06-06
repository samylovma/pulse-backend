from collections.abc import AsyncGenerator

import pytest
from litestar import Litestar
from litestar.testing import AsyncTestClient

from pulse_backend.app import create_app


@pytest.fixture()
async def client() -> AsyncGenerator[AsyncTestClient[Litestar], None]:
    async with AsyncTestClient(create_app()) as client:
        yield client
