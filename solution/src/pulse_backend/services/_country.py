from advanced_alchemy import SQLAlchemyAsyncRepositoryService
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository

from pulse_backend.db_schema import Country


class CountryRepository(SQLAlchemyAsyncRepository[Country]):
    model_type = Country


class CountryService(SQLAlchemyAsyncRepositoryService[Country]):
    repository_type = CountryRepository
