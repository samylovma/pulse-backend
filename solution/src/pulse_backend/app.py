from dataclasses import dataclass
from os import getenv
from typing import Any

from litestar import Litestar, Request, Response, status_codes
from litestar.contrib.sqlalchemy.plugins import (
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)
from litestar.exceptions import LitestarException
from sqlalchemy import URL

from pulse_backend.api import create_router
from pulse_backend.jwt import jwt_auth


@dataclass(frozen=True, slots=True)
class ErrorResponse:
    reason: str


def exc_handler(
    _: Request[Any, Any, Any], exc: LitestarException
) -> Response[ErrorResponse]:
    return Response(
        ErrorResponse(exc.detail),
        status_code=getattr(
            exc, "status_code", status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        ),
    )


def create_app() -> Litestar:
    return Litestar(
        route_handlers=(create_router(),),
        exception_handlers={LitestarException: exc_handler},
        on_app_init=(jwt_auth.on_app_init,),
        plugins=(
            SQLAlchemyPlugin(
                config=SQLAlchemyAsyncConfig(
                    connection_string=URL.create(
                        drivername="postgresql+asyncpg",
                        username=getenv("POSTGRES_USERNAME", "postgres"),
                        password=getenv("POSTGRES_PASSWORD"),
                        host=getenv("POSTGRES_HOST", "localhost"),
                        port=int(getenv("POSTGRES_PORT", 5432)),
                        database=getenv("POSTGRES_DATABASE", "postgres"),
                    ).render_as_string(hide_password=False)
                )
            ),
        ),
    )
