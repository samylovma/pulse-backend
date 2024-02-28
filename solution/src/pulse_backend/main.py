from os import getenv

from litestar import Litestar
from litestar.contrib.sqlalchemy.plugins import (
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)
from sqlalchemy import URL

from pulse_backend.controllers import create_router


def create_app() -> Litestar:
    return Litestar(
        route_handlers=(create_router(),),
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
