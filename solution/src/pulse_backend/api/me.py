from typing import Annotated, Any

import bcrypt
import pydantic
from advanced_alchemy.exceptions import IntegrityError
from litestar import Controller, Request, get, patch, post, status_codes
from litestar.di import Provide
from litestar.exceptions import ClientException, PermissionDeniedException
from litestar.security.jwt import Token
from sqlalchemy.ext.asyncio import AsyncSession

from pulse_backend.db_schema import User
from pulse_backend.schemas import UserProfile
from pulse_backend.services import UserService


class UserUpdate(pydantic.BaseModel):
    country_code: Annotated[
        str | None, pydantic.Field(serialization_alias="countryCode")
    ] = None
    is_public: Annotated[
        bool | None, pydantic.Field(serialization_alias="isPublic")
    ] = None
    phone: str | None = None
    image: str | None = None

    # TODO: Validate.


class UpdatePassword(pydantic.BaseModel):
    oldPassword: str
    newPassword: str


async def provide_user_service(db_session: AsyncSession) -> UserService:
    return UserService(session=db_session)


class MeController(Controller):
    path = "/me"
    dependencies = {"user_service": Provide(provide_user_service)}  # noqa: RUF012

    @get("/profile")
    async def get(self, request: Request[User, Token, Any]) -> dict[str, Any]:
        return UserProfile.model_validate(request.user).model_dump(
            by_alias=True, exclude_none=True
        )

    @patch("/profile")
    async def update(
        self,
        data: UserUpdate,
        request: Request[User, Token, Any],
        user_service: UserService,
    ) -> UserProfile:
        try:
            user = await user_service.update(
                data.model_dump(exclude_unset=True),
                item_id=request.user.login,
                auto_commit=True,
                id_attribute="login",
            )
            return UserProfile.model_validate(user)
        except IntegrityError as e:
            raise ClientException(
                status_code=status_codes.HTTP_409_CONFLICT
            ) from e

    @post("/updatePassword")
    async def update_password(
        self,
        data: UpdatePassword,
        request: Request[User, Token, Any],
        user_service: UserService,
    ) -> dict[str, Any]:
        if bcrypt.checkpw(
            data.oldPassword.encode(encoding="utf-8"),
            request.user.hashed_password,
        ):
            await user_service.update(
                {"password": data.newPassword},
                item_id=request.user.login,
                auto_commit=True,
                id_attribute="login",
            )
            return {"status": "ok"}
        raise PermissionDeniedException("Invalid password")
