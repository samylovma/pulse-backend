import uvicorn
from litestar import Litestar, get


@get("/api/ping")
async def ping() -> dict[str, str]:
    return {"status": "ok"}


def create_app() -> Litestar:
    return Litestar(route_handlers=(ping,))


if __name__ == "__main__":
    uvicorn.run(create_app())
