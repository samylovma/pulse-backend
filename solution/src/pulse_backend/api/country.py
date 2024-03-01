import enum
from collections.abc import Sequence

import advanced_alchemy
import litestar
from advanced_alchemy.filters import CollectionFilter, FilterTypes, OrderBy
from litestar import Controller, get
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession

from pulse_backend.db_schema import Country
from pulse_backend.services import CountryService


class RegionEnum(enum.StrEnum):
    europe = "Europe"
    africa = "Africa"
    americas = "Americas"
    oceania = "Oceania"
    asia = "Asia"


class ReadDTO(SQLAlchemyDTO[Country]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
        }
    )

    region: RegionEnum


async def provide_country_service(db_session: AsyncSession) -> CountryService:
    return CountryService(session=db_session)


class CountryController(Controller):
    path = "/countries"
    dependencies = {"country_service": Provide(provide_country_service)}
    return_dto = ReadDTO

    @get()
    async def list_countries(
        self,
        country_service: CountryService,
        region: list[RegionEnum] | None = None,
    ) -> Sequence[Country]:
        filters: list[FilterTypes] = []
        filters.append(OrderBy(field_name="alpha2", sort_order="asc"))
        if region:
            filters.append(
                CollectionFilter(field_name="region", values=region)
            )
        return await country_service.list(*filters)

    @get("/{alpha2:str}")
    async def get_country(
        self, country_service: CountryService, alpha2: str
    ) -> Country:
        try:
            return await country_service.get_one(alpha2=alpha2)
        except advanced_alchemy.exceptions.NotFoundError as e:
            raise litestar.exceptions.NotFoundException(
                "Country not found"
            ) from e
