from typing import Any, Self

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy import delete

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
        self: Self, data: User | dict[str, Any], operation: str | None = None
    ) -> User:
        if isinstance(data, dict):
            password = data.pop("password", None)
            if isinstance(password, str):
                data["hashed_password"] = hash_password(password)
        return await super().to_model(data=data, operation=operation)


class FriendService(SQLAlchemyAsyncRepositoryService[Friend]):
    repository_type = FriendRepository


class PostService(SQLAlchemyAsyncRepositoryService[Post]):
    repository_type = PostRepository


class SessionService(SQLAlchemyAsyncRepositoryService[Session]):
    repository_type = SessionRepository

    async def deactivate(self: Self, user_login: str) -> None:
        await self.repository.session.execute(
            delete(Session).where(Session.user_login == user_login)
        )
        await self.repository._flush_or_commit(auto_commit=None)
