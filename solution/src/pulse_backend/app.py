from dataclasses import dataclass
from os import getenv
from typing import Any

from litestar import Litestar, Request, Response
from litestar.contrib.sqlalchemy.plugins import (
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)
from litestar.exceptions import HTTPException
from sqlalchemy import URL

from pulse_backend import sessions
from pulse_backend.api import create_router


@dataclass(frozen=True, slots=True)
class ErrorResponse:
    reason: str


def exc_handler(
    _: Request[Any, Any, Any], exc: HTTPException
) -> Response[ErrorResponse]:
    return Response(
        ErrorResponse(exc.detail),
        status_code=exc.status_code,
    )


def create_app() -> Litestar:
    return Litestar(
        route_handlers=(create_router(),),
        exception_handlers={HTTPException: exc_handler},
        on_app_init=(sessions.auth.on_app_init,),
        plugins=(
            SQLAlchemyPlugin(
                config=SQLAlchemyAsyncConfig(
                    connection_string=URL.create(
                        drivername="postgresql+asyncpg",
                        username=getenv("POSTGRES_USERNAME", "postgres"),
                        password=getenv("POSTGRES_PASSWORD"),
                        host=getenv("POSTGRES_HOST", "localhost"),
                        port=int(getenv("POSTGRES_PORT", "5432")),
                        database=getenv("POSTGRES_DATABASE", "postgres"),
                    ).render_as_string(hide_password=False)
                )
            ),
        ),
    )
