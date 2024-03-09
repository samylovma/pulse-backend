from datetime import UTC, datetime, timedelta
from typing import Any

from advanced_alchemy.exceptions import IntegrityError
from litestar import Controller, post
from litestar.di import Provide
from litestar.exceptions import (
    ClientException,
    NotAuthorizedException,
    ValidationException,
)
from litestar.status_codes import HTTP_200_OK, HTTP_409_CONFLICT

from pulse_backend import sessions
from pulse_backend.crypt import check_password, hash_password
from pulse_backend.db_models import Session, User
from pulse_backend.dependencies import (
    provide_country_service,
    provide_session_service,
    provide_user_service,
)
from pulse_backend.schema import RegisterUser, SignInUser, UserProfile
from pulse_backend.services import (
    CountryService,
    SessionService,
    UserService,
)


class AuthController(Controller):
    dependencies = {  # noqa: RUF012
        "country_service": Provide(provide_country_service),
        "user_service": Provide(provide_user_service),
        "session_service": Provide(provide_session_service),
    }

    @post("/api/auth/register")
    async def register(
        self,
        data: RegisterUser,
        country_service: CountryService,
        user_service: UserService,
    ) -> dict[str, Any]:
        country = await country_service.get_one_or_none(
            alpha2=data.country_code
        )
        if country is None:
            raise ValidationException("Country not found")

        user = User(
            login=data.login,
            email=data.email,
            hashed_password=hash_password(data.password),
            country_code=data.country_code,
            is_public=data.is_public,
            phone=data.phone,
            image=data.image,
        )
        try:
            user = await user_service.create(user, auto_commit=True)
        except IntegrityError as e:
            raise ClientException(status_code=HTTP_409_CONFLICT) from e

        return {
            "profile": UserProfile.model_validate(user).model_dump(
                exclude_none=True
            )
        }

    @post("/api/auth/sign-in", status_code=HTTP_200_OK)
    async def sign_in(
        self,
        data: SignInUser,
        user_service: UserService,
        session_service: SessionService,
    ) -> dict[str, Any]:
        user = await user_service.get_one_or_none(login=data.login)
        if user is None:
            raise NotAuthorizedException("User doesn't exist")
        if not check_password(data.password, user.hashed_password):
            raise NotAuthorizedException("Invalid password")
        session = Session(
            exp=(datetime.now(UTC) + timedelta(hours=1)), user_login=user.login
        )
        await session_service.create(session, auto_commit=True)
        token = sessions.auth.create_token(session)
        return {"token": token}
