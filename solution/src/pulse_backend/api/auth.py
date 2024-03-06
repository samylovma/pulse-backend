from typing import Any

import bcrypt
from advanced_alchemy.exceptions import IntegrityError
from litestar import Controller, post, status_codes
from litestar.di import Provide
from litestar.exceptions import (
    ClientException,
    NotAuthorizedException,
    ValidationException,
)

from pulse_backend.deps import (
    provide_country_service,
    provide_token_service,
    provide_user_service,
)
from pulse_backend.schema import RegisterUser, SignInUser, UserProfile
from pulse_backend.services import CountryService, TokenService, UserService


class AuthController(Controller):
    dependencies = {  # noqa: RUF012
        "country_service": Provide(provide_country_service),
        "user_service": Provide(provide_user_service),
        "token_service": Provide(provide_token_service),
    }

    @post("/api/auth/register")
    async def register(
        self,
        data: RegisterUser,
        country_service: CountryService,
        user_service: UserService,
    ) -> dict[str, Any]:
        country = await country_service.get_one_or_none(
            alpha2=data.countryCode
        )
        if country is None:
            raise ValidationException("Country not found")

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
        self,
        data: SignInUser,
        user_service: UserService,
        token_service: TokenService,
    ) -> dict[str, Any]:
        user = await user_service.get_one_or_none(login=data.login)
        if user is None:
            raise NotAuthorizedException("User doesn't exist")

        if bcrypt.checkpw(
            data.password.encode(encoding="utf-8"), user.hashedPassword
        ):
            token = await token_service.create_token(data.login)
            return {"token": token}

        raise NotAuthorizedException("Invalid password")
