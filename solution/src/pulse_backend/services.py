from typing import Any

import bcrypt
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

    async def to_model(
        self, data: User | dict[str, Any], operation: str | None = None
    ) -> User:
        if isinstance(data, dict):
            password: str | None = data.pop("password", None)
            if password is not None:
                data["hashed_password"] = bcrypt.hashpw(
                    password.encode(encoding="utf-8"), bcrypt.gensalt()
                )
        return await super().to_model(data, operation)
