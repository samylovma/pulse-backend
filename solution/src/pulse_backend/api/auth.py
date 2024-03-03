from datetime import timedelta
from typing import Any

import bcrypt
from advanced_alchemy.exceptions import IntegrityError, NotFoundError
from litestar import Controller, post, status_codes
from litestar.di import Provide
from litestar.exceptions import (
    ClientException,
    NotAuthorizedException,
    ValidationException,
)

from pulse_backend.jwt import jwt_auth
from pulse_backend.schema import UserProfile, RegisterUser, SignInUser
from pulse_backend.services import UserService, CountryService
from pulse_backend.deps import provide_user_service, provide_country_service


class AuthController(Controller):
    dependencies = {
        "country_service": Provide(provide_country_service),
        "user_service": Provide(provide_user_service),
    }  # noqa: RUF012

    @post("/api/auth/register")
    async def register(
        self,
        data: RegisterUser,
        country_service: CountryService,
        user_service: UserService,
    ) -> dict[str, Any]:
        try:
            await country_service.get(
                item_id=data.countryCode, id_attribute="alpha2"
            )
        except NotFoundError as e:
            raise ValidationException("Country not found") from e

        try:
            user = await user_service.create(
                data.model_dump(), auto_commit=True
            )
            return {
                "profile": UserProfile.model_validate(user).model_dump(
                    exclude_none=True
                )
            }
        except IntegrityError as e:
            raise ClientException(
                status_code=status_codes.HTTP_409_CONFLICT
            ) from e

    @post("/api/auth/sign-in", status_code=status_codes.HTTP_200_OK)
    async def sign_in(
        self, data: SignInUser, user_service: UserService
    ) -> dict[str, Any]:
        try:
            user = await user_service.get_one(login=data.login)
        except NotFoundError as e:
            raise NotAuthorizedException("User doesn't exist") from e

        if bcrypt.checkpw(
            data.password.encode(encoding="utf-8"), user.hashedPassword
        ):
            return {
                "token": jwt_auth.create_token(
                    identifier=user.login, token_expiration=timedelta(hours=24)
                )
            }

        raise NotAuthorizedException("Invalid password")
