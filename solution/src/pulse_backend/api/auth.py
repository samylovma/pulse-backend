from typing import Annotated, cast

import bcrypt
import pydantic
import sqlalchemy
from litestar import Controller, post, status_codes
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.di import Provide
from litestar.exceptions import ClientException
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from pulse_backend.db_schema import User
from pulse_backend.services import UserService


class RegisterUser(pydantic.BaseModel):
    login: str
    email: str
    password: bytes
    country_code: str = pydantic.Field(alias="countryCode")
    is_public: bool = pydantic.Field(alias="isPublic")
    phone: str | None = None
    image: str | None = None

    # TODO: Validate.


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
        self, data: RegisterUser, user_service: UserService
    ) -> User:
        data.password = bcrypt.hashpw(data.password, bcrypt.gensalt())
        try:
            return cast(
                User,
                await user_service.repository.session.scalar(
                    insert(User).returning(User), data.model_dump()
                ),
            )
        except sqlalchemy.exc.IntegrityError as e:
            raise ClientException(
                status_code=status_codes.HTTP_409_CONFLICT
            ) from e
