from typing import Any

from advanced_alchemy.exceptions import IntegrityError
from litestar import Controller, Request, get, patch, post, status_codes
from litestar.di import Provide
from litestar.exceptions import (
    ClientException,
    PermissionDeniedException,
    ValidationException,
)
from litestar.security.jwt import Token
from litestar.status_codes import HTTP_200_OK
from sqlalchemy import delete

from pulse_backend.crypt import check_password
from pulse_backend.db.models import Session, User
from pulse_backend.dependencies import (
    provide_country_service,
    provide_session_service,
    provide_user_service,
)
from pulse_backend.schema import UpdatePassword, UpdateUser, UserProfile
from pulse_backend.services import CountryService, SessionService, UserService


class MeController(Controller):
    dependencies = {  # noqa: RUF012
        "country_service": Provide(provide_country_service),
        "user_service": Provide(provide_user_service),
        "session_service": Provide(provide_session_service),
    }

    @get("/api/me/profile")
    async def get(self, request: Request[User, Token, Any]) -> dict[str, Any]:
        return UserProfile.model_validate(request.user).model_dump(
            exclude_none=True
        )

    @patch("/api/me/profile", status_code=HTTP_200_OK)
    async def update(
        self,
        data: UpdateUser,
        request: Request[User, Token, Any],
        country_service: CountryService,
        user_service: UserService,
    ) -> dict[str, Any]:
        if data.countryCode:
            country = await country_service.get_one(alpha2=data.countryCode)
            if country is None:
                raise ValidationException("Country not found")

        try:
            user = await user_service.update(
                data.model_dump(exclude_unset=True),
                item_id=request.user.id,
                auto_commit=True,
            )
            return UserProfile.model_validate(user).model_dump(
                exclude_none=True
            )
        except IntegrityError as e:
            raise ClientException(
                status_code=status_codes.HTTP_409_CONFLICT
            ) from e

    @post("/api/me/updatePassword", status_code=HTTP_200_OK)
    async def update_password(
        self,
        data: UpdatePassword,
        request: Request[User, Token, Any],
        user_service: UserService,
        session_service: SessionService,
    ) -> dict[str, Any]:
        if not check_password(data.oldPassword, request.user.hashed_password):
            raise PermissionDeniedException("Invalid password")
        await session_service.repository.session.execute(
            delete(Session).where(Session.user_id == request.user.id)
        )
        await session_service.repository.session.commit()
        await user_service.update(
            {"password": data.newPassword},
            item_id=request.user.id,
            auto_commit=True,
        )
        return {"status": "ok"}
