from typing import Any
from datetime import timedelta

import bcrypt
from advanced_alchemy import SQLAlchemyAsyncRepositoryService
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.security.jwt import BaseJWTAuth
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from pulse_backend.db_schema import Country, User, Token


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
                data["hashedPassword"] = bcrypt.hashpw(
                    password.encode(encoding="utf-8"), bcrypt.gensalt()
                )
        return await super().to_model(data, operation)


class TokenRepository(SQLAlchemyAsyncRepository[Token]):
    model_type = Token


class _TokenService(SQLAlchemyAsyncRepositoryService[Token]):
    repository_type = TokenRepository


class TokenService:
    def __init__(
        self, db_session: AsyncSession, jwt_auth: BaseJWTAuth[User]
    ) -> None:
        self.jwt_auth: BaseJWTAuth[User] = jwt_auth

        self.__service: _TokenService = _TokenService(session=db_session)

    async def create_token(self, user_login: str) -> str:
        token: str = self.jwt_auth.create_token(
            identifier=user_login, token_expiration=timedelta(hours=24)
        )
        await self.__service.create(
            Token(token=token, user_login=user_login, is_revoked=False),
            auto_commit=True,
        )
        return token

    async def get(self, token: str) -> Token | None:
        return await self.__service.get_one_or_none(token=token)

    async def revoke_user(self, user_login: str) -> None:
        await self.__service.repository.session.execute(
            (
                update(Token)
                .where(Token.user_login == user_login)
                .values(is_revoked=True)
            )
        )
        await self.__service.repository.session.commit()
