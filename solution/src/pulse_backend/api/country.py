from typing import Annotated, Any

from advanced_alchemy.filters import CollectionFilter, FilterTypes, OrderBy
from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.params import Parameter

from pulse_backend.deps import provide_country_service
from pulse_backend.schema import Country, CountryRegion
from pulse_backend.services import CountryService


class CountryController(Controller):
    dependencies = {  # noqa: RUF012
        "country_service": Provide(provide_country_service)
    }

    @get("/api/countries")
    async def list_countries(
        self,
        country_service: CountryService,
        region: list[CountryRegion] | None = None,
    ) -> list[dict[str, Any]]:
        filters: list[FilterTypes] = []
        filters.append(OrderBy(field_name="alpha2", sort_order="asc"))
        if region:
            filters.append(
                CollectionFilter(field_name="region", values=region)
            )
        countries = await country_service.list(*filters)
        return [
            Country.model_validate(country).model_dump(exclude_none=True)
            for country in countries
        ]

    @get("/api/countries/{alpha2:str}")
    async def get_country(
        self,
        country_service: CountryService,
        alpha2: Annotated[
            str,
            Parameter(max_length=2, pattern=r"[a-zA-Z]{2}"),
        ],
    ) -> dict[str, Any]:
        country = await country_service.get_one_or_none(alpha2=alpha2)
        if country is None:
            raise NotFoundException("Country not found")
        return Country.model_validate(country).model_dump(exclude_none=True)
