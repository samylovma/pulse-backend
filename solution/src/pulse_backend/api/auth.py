from dataclasses import dataclass
from datetime import timedelta
from typing import Annotated, Any

import bcrypt
import pydantic
from advanced_alchemy.exceptions import IntegrityError, NotFoundError
from litestar import Controller, post, status_codes
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.di import Provide
from litestar.exceptions import ClientException, NotAuthorizedException
from sqlalchemy.ext.asyncio import AsyncSession

from pulse_backend.db_schema import User
from pulse_backend.jwt import jwt_auth
from pulse_backend.services import UserService


class Register(pydantic.BaseModel):
    login: str
    email: str
    password: str
    country_code: str = pydantic.Field(alias="countryCode")
    is_public: bool = pydantic.Field(alias="isPublic")
    phone: str | None = None
    image: str | None = None

    # TODO: Validate.


@dataclass(frozen=True, slots=True)
class SignIn:
    login: str
    password: str


@dataclass(frozen=True, slots=True)
class SuccessSignIn:
    token: str


ReadDTO = SQLAlchemyDTO[
    Annotated[
        User,
        SQLAlchemyDTOConfig(
            exclude={
                "hashed_password",
            }
        ),
    ]
]


class UserProfile(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    login: str
    email: str
    country_code: str = pydantic.Field(serialization_alias="countryCode")
    is_public: bool = pydantic.Field(serialization_alias="isPublic")
    phone: str | None
    image: str | None


async def provide_user_service(db_session: AsyncSession) -> UserService:
    return UserService(session=db_session)


class AuthController(Controller):
    path = "/auth"
    dependencies = {"user_service": Provide(provide_user_service)}  # noqa: RUF012

    @post("/register")
    async def register(
        self, data: Register, user_service: UserService
    ) -> dict[str, Any]:
        try:
            user = await user_service.create(
                data.model_dump(), auto_commit=True
            )
            return {
                "profile": UserProfile.model_validate(user).model_dump(
                    by_alias=True, exclude_none=True
                )
            }
        except IntegrityError as e:
            raise ClientException(
                status_code=status_codes.HTTP_409_CONFLICT
            ) from e

    # TODO: Refactor the method. Move logic to UserService.
    @post("/sign-in", status_code=status_codes.HTTP_200_OK)
    async def sign_in(
        self, data: SignIn, user_service: UserService
    ) -> SuccessSignIn:
        try:
            user: User = await user_service.get_one(login=data.login)
        except NotFoundError as e:
            raise NotAuthorizedException(
                f'User "{data.login}" doesn\'t exist'
            ) from e

        if bcrypt.checkpw(
            data.password.encode(encoding="utf-8"), user.hashed_password
        ):
            return SuccessSignIn(
                token=jwt_auth.create_token(
                    identifier=user.login, token_expiration=timedelta(hours=24)
                )
            )
        raise NotAuthorizedException(
            f'Invalid password for user "{user.login}"'
        )
