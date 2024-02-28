from os import getenv
from typing import Literal

import pydantic
from advanced_alchemy.filters import CollectionFilter, FilterTypes, OrderBy
from litestar import Litestar, MediaType, Response, Router, get, status_codes
from litestar.contrib.sqlalchemy.base import CommonTableAttributes
from litestar.contrib.sqlalchemy.plugins import (
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.controller import Controller
from litestar.di import Provide
from litestar.openapi import ResponseSpec
from sqlalchemy import TEXT, URL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Country(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    name: str
    alpha2: str
    alpha3: str
    region: str


class ErrorResponse(pydantic.BaseModel):
    reason: str


class BaseModel(DeclarativeBase):
    ...


class CountryModel(CommonTableAttributes, BaseModel):
    __tablename__ = "countries"  # type: ignore[assignment]

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(TEXT())
    alpha2: Mapped[str] = mapped_column(TEXT())
    alpha3: Mapped[str] = mapped_column(TEXT())
    region: Mapped[str] = mapped_column(TEXT())


class CountryRepository(SQLAlchemyAsyncRepository[CountryModel]):
    model_type = CountryModel


async def provide_country_repo(db_session: AsyncSession) -> CountryRepository:
    return CountryRepository(session=db_session)


@get("/ping", media_type=MediaType.TEXT)
async def ping() -> Literal["ok"]:
    return "ok"


class CountryController(Controller):
    path = "/countries"
    dependencies = {"country_repo": Provide(provide_country_repo)}

    @get()
    async def list_countries(
        self, country_repo: CountryRepository, region: list[str] | None = None
    ) -> list[Country]:
        filters: list[FilterTypes] = []
        filters.append(OrderBy(field_name="alpha2", sort_order="asc"))
        if region:
            filters.append(
                CollectionFilter(field_name="region", values=region)
            )
        countries = await country_repo.list(*filters)
        return [Country.model_validate(country) for country in countries]

    @get(
        "/{alpha2:str}",
        responses={
            404: ResponseSpec(
                data_container=ErrorResponse, description="Country not found"
            ),
        },
    )
    async def get_country(
        self, country_repo: CountryRepository, alpha2: str
    ) -> Country | Response[ErrorResponse]:
        country = await country_repo.get_one_or_none(alpha2=alpha2)
        if isinstance(country, CountryModel):
            return Country.model_validate(country)
        else:
            return Response(
                content=ErrorResponse(reason=f'Country "{alpha2}" not found.'),
                status_code=status_codes.HTTP_404_NOT_FOUND,
            )


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
