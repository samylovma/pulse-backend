from typing import Literal

from litestar import MediaType, get


@get("/api/ping", media_type=MediaType.TEXT)
async def ping() -> Literal["ok"]:
    return "ok"
