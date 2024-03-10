from typing import Any

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from pulse_backend.crypt import hash_password
from pulse_backend.db_models import Country, Friend, Post, Session, User
from pulse_backend.repositories import (
    CountryRepository,
    FriendRepository,
    PostRepository,
    SessionRepository,
    UserRepository,
)


class CountryService(SQLAlchemyAsyncRepositoryService[Country]):
    repository_type = CountryRepository


class UserService(SQLAlchemyAsyncRepositoryService[User]):
    repository_type = UserRepository

    async def to_model(
        self, data: User | dict[str, Any], operation: str | None = None
    ) -> User:
        if isinstance(data, dict) and "password" in data:
            password = data.pop("password")
            if isinstance(password, str):
                data["hashed_password"] = hash_password(password)
        return await super().to_model(data=data, operation=operation)


class FriendService(SQLAlchemyAsyncRepositoryService[Friend]):
    repository_type = FriendRepository


class PostService(SQLAlchemyAsyncRepositoryService[Post]):
    repository_type = PostRepository


class SessionService(SQLAlchemyAsyncRepositoryService[Session]):
    repository_type = SessionRepository
