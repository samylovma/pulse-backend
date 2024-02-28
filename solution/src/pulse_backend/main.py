from os import getenv
from typing import Literal

import pydantic
from litestar import Litestar, MediaType, Router, get
from litestar.contrib.sqlalchemy.base import CommonTableAttributes
from litestar.contrib.sqlalchemy.plugins import (
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.controller import Controller
from litestar.di import Provide
from sqlalchemy import TEXT, URL, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseORM(DeclarativeBase):
    ...


class CountryORM(CommonTableAttributes, BaseORM):
    __tablename__ = "countries"  # type: ignore[assignment]

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(TEXT())
    alpha2: Mapped[str] = mapped_column(TEXT())
    alpha3: Mapped[str] = mapped_column(TEXT())
    region: Mapped[str] = mapped_column(TEXT())


class Country(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    name: str
    alpha2: str
    alpha3: str
    region: str


class CountryRepository(SQLAlchemyAsyncRepository[CountryORM]):
    model_type = CountryORM


async def provide_country_repo(db_session: AsyncSession) -> CountryRepository:
    return CountryRepository(session=db_session)


@get("/ping", media_type=MediaType.TEXT)
async def ping() -> Literal["ok"]:
    return "ok"


class CountryController(Controller):
    path = "/countries"
    dependencies = {"country_repo": Provide(provide_country_repo)}

    @get()
    async def countries(
        self, country_repo: CountryRepository, region: str | None = None
    ) -> list[Country]:
        if region:
            countries = await country_repo.list(
                statement=select(CountryORM).where(CountryORM.region == region)
            )
        else:
            countries = await country_repo.list()
        return [Country.model_validate(country) for country in countries]


def create_app() -> Litestar:
    return Litestar(
        route_handlers=(
            Router(path="/api", route_handlers=(ping, CountryController)),
        ),
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
