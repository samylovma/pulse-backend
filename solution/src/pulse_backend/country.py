import enum

from advanced_alchemy import SQLAlchemyAsyncRepositoryService
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository

from pulse_backend.db_schema import Country


class CountryRepository(SQLAlchemyAsyncRepository[Country]):
    model_type = Country


class CountryService(SQLAlchemyAsyncRepositoryService[Country]):
    repository_type = CountryRepository


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
