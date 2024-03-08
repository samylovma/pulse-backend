from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryReadService

from pulse_backend.db.models import Country


class CountryRepository(SQLAlchemyAsyncRepository[Country]):
    model_type = Country


class CountryService(SQLAlchemyAsyncRepositoryReadService[Country]):
    repository_type = CountryRepository
