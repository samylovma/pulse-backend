from datetime import timedelta
from typing import Annotated

import bcrypt
import pydantic
from advanced_alchemy.exceptions import NotFoundError
from litestar import Controller, post, status_codes
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.di import Provide
from litestar.exceptions import NotAuthorizedException
from sqlalchemy.ext.asyncio import AsyncSession

from pulse_backend.db_schema import User
from pulse_backend.jwt import jwt_auth
from pulse_backend.services import UserService


class Register(pydantic.BaseModel):
    login: str
    email: str
    password: bytes
    country_code: str = pydantic.Field(alias="countryCode")
    is_public: bool = pydantic.Field(alias="isPublic")
    phone: str | None = None
    image: str | None = None

    # TODO: Validate.


class SignIn(pydantic.BaseModel):
    login: str
    password: bytes


class SuccessSignIn(pydantic.BaseModel):
    token: str


ReadDTO = SQLAlchemyDTO[
    Annotated[
        User,
        SQLAlchemyDTOConfig(
            exclude={
                "password",
            }
        ),
    ]
]


async def provide_user_service(db_session: AsyncSession) -> UserService:
    return UserService(session=db_session)


class AuthController(Controller):
    path = "/auth"
    dependencies = {"user_service": Provide(provide_user_service)}

    @post("/register", return_dto=ReadDTO)
    async def register(
        self, data: Register, user_service: UserService
    ) -> User:
        data.password = bcrypt.hashpw(data.password, bcrypt.gensalt())
        return await user_service.create(data.model_dump(), auto_commit=True)

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

        if bcrypt.checkpw(data.password, user.password):
            return SuccessSignIn(
                token=jwt_auth.create_token(
                    identifier=user.login, token_expiration=timedelta(hours=24)
                )
            )
        raise NotAuthorizedException(
            f'Invalid password for user "{user.login}"'
        )
