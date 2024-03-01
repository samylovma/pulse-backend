from advanced_alchemy import SQLAlchemyAsyncRepositoryService
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository

from pulse_backend.db_schema import Country, User


class CountryRepository(SQLAlchemyAsyncRepository[Country]):
    model_type = Country


class CountryService(SQLAlchemyAsyncRepositoryService[Country]):
    repository_type = CountryRepository


class UserRepository(SQLAlchemyAsyncRepository[User]):
    model_type = User


class UserService(SQLAlchemyAsyncRepositoryService[User]):
    repository_type = UserRepository
