from typing import Any

from advanced_alchemy.exceptions import IntegrityError
from litestar import Controller, Request, get, patch, post
from litestar.di import Provide
from litestar.exceptions import (
    ClientException,
    PermissionDeniedException,
    ValidationException,
)
from litestar.status_codes import HTTP_200_OK, HTTP_409_CONFLICT
from sqlalchemy import delete

from pulse_backend.crypt import check_password, hash_password
from pulse_backend.db_models import Session, User
from pulse_backend.dependencies import (
    provide_country_service,
    provide_session_service,
    provide_user_service,
)
from pulse_backend.dto import UserDTO
from pulse_backend.schemas import UpdatePassword, UpdateUser
from pulse_backend.services import CountryService, SessionService, UserService


class MeController(Controller):
    dependencies = {  # noqa: RUF012
        "country_service": Provide(provide_country_service),
        "user_service": Provide(provide_user_service),
        "session_service": Provide(provide_session_service),
    }

    @get("/api/me/profile", return_dto=UserDTO)
    async def get(self, request: Request[User, Session, Any]) -> User:
        return request.user

    @patch("/api/me/profile", status_code=HTTP_200_OK, return_dto=UserDTO)
    async def update(
        self,
        data: UpdateUser,
        request: Request[User, Session, Any],
        country_service: CountryService,
        user_service: UserService,
    ) -> User:
        if isinstance(data.country_code, str) and not await country_service.exists(
            alpha2=data.country_code
        ):
            raise ValidationException("Country not found")
        try:
            return await user_service.update(
                data.model_dump(exclude_unset=True),
                item_id=request.user.login,
                auto_commit=True,
            )
        except IntegrityError as e:
            raise ClientException(status_code=HTTP_409_CONFLICT) from e

    @post("/api/me/updatePassword", status_code=HTTP_200_OK)
    async def update_password(
        self,
        data: UpdatePassword,
        request: Request[User, Session, Any],
        user_service: UserService,
        session_service: SessionService,
    ) -> dict[str, str]:
        if not check_password(data.oldPassword, request.user.hashed_password):
            raise PermissionDeniedException("Invalid password")

        stmt = delete(Session).where(Session.user_login == request.user.login)
        await session_service.repository.session.execute(stmt)
        await session_service.repository.session.commit()

        request.user.hashed_password = hash_password(data.newPassword)
        await user_service.update(request.user, auto_commit=True)

        return {"status": "ok"}
