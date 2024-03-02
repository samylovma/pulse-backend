from os import getenv
from typing import Any

from litestar.connection import ASGIConnection
from litestar.security.jwt import JWTAuth, Token

from pulse_backend.db_schema import User
from pulse_backend.services import UserService


async def retrieve_user_handler(
    token: Token, connection: ASGIConnection[Any, Any, Any, Any]
) -> User | None:
    db_session = await connection.app.dependencies["db_session"](
        state=connection.app.state, scope=connection.scope
    )
    user_service = UserService(session=db_session)
    user = await user_service.get_one_or_none(login=token.sub)
    return user


jwt_auth = JWTAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=getenv("RANDOM_SECRET", "token"),
    exclude=[
        "/api/ping",
        "/api/countries",
        "/api/auth/register",
        "/api/auth/sign-in",
    ],
)
