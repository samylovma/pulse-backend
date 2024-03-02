from typing import Any

from litestar.connection import ASGIConnection
from litestar.security.jwt import JWTAuth, Token

from pulse_backend.db_schema import User
from pulse_backend.services import UserService


async def retrieve_user_handler(
    token: Token, connection: ASGIConnection[Any, Any, Any, Any]
) -> User | None:
    db_session = await connection.app.dependencies["db_session"]()
    user_service = UserService(session=db_session)
    return await user_service.get_one_or_none(login=token.sub)


jwt_auth = JWTAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    # TODO: Inject/generate token_secret.
    token_secret="12345",
    exclude=[
        "/api/ping",
        "/api/countries",
        "/api/auth/register",
        "/api/auth/sign-in",
    ],
)
