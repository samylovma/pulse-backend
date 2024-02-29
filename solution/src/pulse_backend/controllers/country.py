import advanced_alchemy
import litestar
from advanced_alchemy.filters import CollectionFilter, FilterTypes, OrderBy
from litestar import Controller, get
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession

from pulse_backend.domain.country import (
    Country,
    CountryDTO,
    CountryRepository,
    RegionEnum,
)


async def provide_country_repo(db_session: AsyncSession) -> CountryRepository:
    return CountryRepository(session=db_session)


class CountryController(Controller):
    path = "/countries"
    dependencies = {"country_repo": Provide(provide_country_repo)}
    return_dto = CountryDTO

    @get()
    async def list_countries(
        self,
        country_repo: CountryRepository,
        region: list[RegionEnum] | None = None,
    ) -> list[Country]:
        filters: list[FilterTypes] = []
        filters.append(OrderBy(field_name="alpha2", sort_order="asc"))
        if region:
            filters.append(
                CollectionFilter(field_name="region", values=region)
            )
        return await country_repo.list(*filters)

    @get("/{alpha2:str}")
    async def get_country(
        self, country_repo: CountryRepository, alpha2: str
    ) -> Country:
        try:
            return await country_repo.get_one(alpha2=alpha2)
        except advanced_alchemy.exceptions.NotFoundError as e:
            raise litestar.exceptions.NotFoundException() from e
