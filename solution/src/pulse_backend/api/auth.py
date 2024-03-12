from datetime import UTC, datetime, timedelta

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
from pulse_backend.crypt import check_password
from pulse_backend.db_models import Session, User
from pulse_backend.dependencies import (
    provide_country_service,
    provide_session_service,
    provide_user_service,
)
from pulse_backend.dto import UserDTO
from pulse_backend.schemas import RegisterUser, SignInUser
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

    @post("/api/auth/register", return_dto=UserDTO)
    async def register(
        self,
        data: RegisterUser,
        country_service: CountryService,
        user_service: UserService,
    ) -> dict[str, User]:
        if not await country_service.exists(alpha2=data.country_code):
            raise ValidationException("Country not found")
        try:
            user = await user_service.create(
                data.model_dump(), auto_commit=True
            )
        except IntegrityError as e:
            raise ClientException(status_code=HTTP_409_CONFLICT) from e
        # TODO: Exclude null fields to follow the spec.
        return {"profile": user}

    @post("/api/auth/sign-in", status_code=HTTP_200_OK)
    async def sign_in(
        self,
        data: SignInUser,
        user_service: UserService,
        session_service: SessionService,
    ) -> dict[str, str]:
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
