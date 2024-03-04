from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import bcrypt
from advanced_alchemy import SQLAlchemyAsyncRepositoryService
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.security.jwt import BaseJWTAuth
from litestar.security.jwt import Token as JWTToken
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from pulse_backend.db_schema import Country, Friend, Post, Token, User


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


class FriendRepository(SQLAlchemyAsyncRepository[Friend]):
    model_type = Friend


class FriendService(SQLAlchemyAsyncRepositoryService[Friend]):
    repository_type = FriendRepository


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
        id_ = uuid4()
        token = JWTToken(
            exp=(datetime.now(UTC) + timedelta(hours=24)),
            sub=user_login,
            iat=datetime.now(UTC),
            jti=str(id_),
        )
        await self.__service.create(
            Token(id=id_, user_login=user_login), auto_commit=True
        )
        return token.encode(
            secret=self.jwt_auth.token_secret,
            algorithm=self.jwt_auth.algorithm,
        )

    async def get(self, jwt_token: JWTToken) -> Token | None:
        return await self.__service.get_one_or_none(id=jwt_token.jti)

    async def revoke_user(self, user_login: str) -> None:
        await self.__service.repository.session.execute(
            delete(Token).where(Token.user_login == user_login)
        )
        await self.__service.repository.session.commit()


class PostRepository(SQLAlchemyAsyncRepository[Post]):
    model_type = Post


class PostService(SQLAlchemyAsyncRepositoryService[Post]):
    repository_type = PostRepository
