from typing import Annotated

import bcrypt
import pydantic
from litestar import Controller, post
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.di import Provide
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
        return await user_service.create(data.model_dump())
