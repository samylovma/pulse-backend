from typing import Any

import bcrypt
from advanced_alchemy.exceptions import IntegrityError, NotFoundError
from litestar import Controller, Request, get, patch, post, status_codes
from litestar.di import Provide
from litestar.exceptions import (
    ClientException,
    PermissionDeniedException,
    ValidationException,
)
from litestar.security.jwt import Token

from pulse_backend.db_schema import User
from pulse_backend.deps import (
    provide_country_service,
    provide_token_service,
    provide_user_service,
)
from pulse_backend.schema import UpdatePassword, UpdateUser, UserProfile
from pulse_backend.services import CountryService, TokenService, UserService


class MeController(Controller):
    dependencies = {
        "country_service": Provide(provide_country_service),
        "user_service": Provide(provide_user_service),
        "token_service": Provide(provide_token_service),
    }

    @get("/api/me/profile")
    async def get(self, request: Request[User, Token, Any]) -> dict[str, Any]:
        return UserProfile.model_validate(request.user).model_dump(
            exclude_none=True
        )

    @patch("/api/me/profile")
    async def update(
        self,
        data: UpdateUser,
        request: Request[User, Token, Any],
        country_service: CountryService,
        user_service: UserService,
    ) -> dict[str, Any]:
        if data.countryCode:
            try:
                await country_service.get_one(alpha2=data.countryCode)
            except NotFoundError as e:
                raise ValidationException("Country not found") from e

        try:
            user = await user_service.update(
                data.model_dump(exclude_unset=True),
                item_id=request.user.login,
                auto_commit=True,
                id_attribute="login",
            )
            return UserProfile.model_validate(user).model_dump(
                exclude_none=True
            )
        except IntegrityError as e:
            raise ClientException(
                status_code=status_codes.HTTP_409_CONFLICT
            ) from e

    @post("/api/me/updatePassword")
    async def update_password(
        self,
        data: UpdatePassword,
        request: Request[User, Token, Any],
        user_service: UserService,
        token_service: TokenService,
    ) -> dict[str, Any]:
        # TODO: Revoke old tokens.
        if bcrypt.checkpw(
            data.oldPassword.encode(encoding="utf-8"),
            request.user.hashedPassword,
        ):
            await user_service.update(
                {"password": data.newPassword},
                item_id=request.user.login,
                auto_commit=True,
                id_attribute="login",
            )
            await token_service.revoke_user(request.user.login)
            return {"status": "ok"}
        raise PermissionDeniedException("Invalid password")
