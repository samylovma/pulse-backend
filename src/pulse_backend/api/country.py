__all__ = ("CountryController",)

from collections.abc import Sequence
from typing import Annotated, Self

from advanced_alchemy.filters import CollectionFilter, FilterTypes, OrderBy
from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.params import Parameter

from pulse_backend.db_models import Country
from pulse_backend.dependencies import provide_country_service
from pulse_backend.dto import CountryDTO
from pulse_backend.schemas import CountryRegion
from pulse_backend.services import CountryService


class CountryController(Controller):
    dependencies = {  # noqa: RUF012
        "country_service": Provide(provide_country_service),
    }
    return_dto = CountryDTO

    @get("/api/countries")
    async def list_countries(
        self: Self,
        country_service: CountryService,
        region: list[CountryRegion] | None = None,
    ) -> Sequence[Country]:
        filters: list[FilterTypes] = []
        filters.append(OrderBy(field_name="alpha2", sort_order="asc"))
        if region:
            filters.append(CollectionFilter(field_name="region", values=region))
        return await country_service.list(*filters)

    @get("/api/countries/{alpha2:str}")
    async def get_country(
        self: Self,
        country_service: CountryService,
        alpha2: Annotated[str, Parameter(max_length=2, pattern=r"[a-zA-Z]{2}")],
    ) -> Country:
        country = await country_service.get_one_or_none(alpha2=alpha2)
        if country is None:
            msg = "Country not found"
            raise NotFoundException(msg)
        return country
